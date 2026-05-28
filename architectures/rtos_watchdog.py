from __future__ import annotations

import json
import math
import time
from typing import Any

import requests

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import build_prompt, parse_answer
from core.types import Query, Response


class RTOSWatchdogArchitecture(BaseArchitecture):
    name = "rtos_watchdog"

    def __init__(
        self,
        slm: ModelProvider,
        llm: ModelProvider,
        confidence_threshold: float = 0.60, # Entropi/Güven eşiği (0.0 - 1.0 arası)
        slm_url: str = "auto",
        slm_temperature: float = 0.0,
        llm_temperature: float = 0.0,
        slm_max_tokens: int = 512,
        llm_max_tokens: int = 512,
        task_type: str = "mcq",
    ) -> None:
        super().__init__(slm, llm)
        self.threshold = confidence_threshold
        self.slm_url = slm_url
        self.slm_temperature = slm_temperature
        self.llm_temperature = llm_temperature
        self.slm_max_tokens = slm_max_tokens
        self.llm_max_tokens = llm_max_tokens
        self.task_type = task_type

    def run(self, query: Query) -> Response:
        prompt = build_prompt(query, self.task_type)
        slm_budget = self.slm_max_tokens if self.slm_max_tokens > 0 else 512
        llm_budget = self.llm_max_tokens if self.llm_max_tokens > 0 else 512
        
        t0 = time.perf_counter()
        total_in = total_out = 0
        total_cost = 0.0
        llm_calls = 0
        inference_steps: list[dict[str, Any]] = []

        # ---------------------------------------------------------
        # TIER 1: SLM STREAMING & WATCHDOG INTERRUPT LOOP
        # ---------------------------------------------------------
        # OpenAI Streaming API payload
        payload = {
            "model": self.slm.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.slm_temperature,
            "max_tokens": slm_budget,
            "logprobs": True,
            "top_logprobs": 1,
            "stream": True # CRITICAL: Streaming modunu açıyoruz
        }

        # URL can be overridden from frontend, or 'auto' to use backend config
        if self.slm_url and self.slm_url != "auto" and self.slm_url != "http://localhost:8001/v1":
            slm_url = self.slm_url.rstrip("/")
        else:
            slm_url = getattr(self.slm, "base_url", "http://localhost:8001/v1").rstrip("/")
        
        generated_prefix = ""
        interrupted = False
        slm_tokens = 0
        token_probs = []
        streaming_error = None
        
        headers = {"Content-Type": "application/json"}
        api_key = getattr(self.slm, "api_key", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            # Akışı (Stream) başlat
            with requests.post(f"{slm_url}/chat/completions", json=payload, headers=headers, stream=True, timeout=10) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if not line:
                        continue
                        
                    decoded_line = line.decode('utf-8')
                    if decoded_line == "data: [DONE]":
                        break
                        
                    if decoded_line.startswith("data: "):
                        chunk_data = json.loads(decoded_line[6:])
                        delta = chunk_data["choices"][0].get("delta", {})
                        logprobs_data = chunk_data["choices"][0].get("logprobs", {})
                        
                        # Yeni üretilen kelimeyi al
                        token_text = delta.get("content", "")
                        if not token_text:
                            continue
                            
                        generated_prefix += token_text
                        slm_tokens += 1
                        
                        # WATCHDOG KONTROLÜ: Logprob'u kontrol et
                        if logprobs_data and "content" in logprobs_data and logprobs_data["content"]:
                            logprob_val = logprobs_data["content"][0]["logprob"]
                            # Logprob'u yüzde olasılığa çevir: P = exp(logprob)
                            probability = math.exp(logprob_val)
                            token_probs.append(probability)

                            # EŞİK KONTROLÜ (HARDWARE INTERRUPT SİMÜLASYONU)
                            if probability < self.threshold:
                                print(f"[\U0001f6a8 WATCHDOG INTERRUPT] SLM belirsizliğe düştü! (Token: '{token_text}', Olasılık: {probability:.2f})")
                                interrupted = True
                                break # STREAM'İ VAHŞİCE KES!

        except Exception as e:
            streaming_error = str(e)
            print(f"[HATA] SLM Streaming hatası: {e}")
            interrupted = True # Hata olursa da LLM'e devret

        lat_slm = (time.perf_counter() - t0) * 1000
        total_out += slm_tokens
        
        # Maliyet tahmini (4B model için)
        total_cost += (len(prompt.split()) * 0.10 + slm_tokens * 0.10) / 1_000_000
        
        inference_steps.append({
            "role": "slm_streaming",
            "model_id": self.slm.model_id,
            "latency_ms": lat_slm,
            "tokens_generated_before_interrupt": slm_tokens,
            "interrupted": interrupted
        })

        final_text = generated_prefix

        # ---------------------------------------------------------
        # TIER 2: HEAVY LLM HANDOFF (Eğer kesinti olduysa)
        # ---------------------------------------------------------
        if interrupted:
            llm_calls += 1
            # Ağır modele "Kaldığı yerden devam et" promptu veriyoruz.
            # Not: Tam bir 'completion' modeli değilse, Instruct modellerine 
            # bunu prompt engineering ile yaptırıyoruz.
            handoff_prompt = (
                f"You are a helpful assistant. Complete the reasoning logically from exactly where it left off.\n\n"
                f"Question: {prompt}\n\n"
                f"Started Answer: {generated_prefix}\n"
                f"Continue directly from here:"
            )
            
            llm_text, _, l_in, l_out, l_cost, l_lat = self._timed_generate(
                self.llm, handoff_prompt, temperature=self.llm_temperature, max_tokens=llm_budget
            )
            
            # SLM'in doğru ürettiği kısım ile LLM'in tamamladığı kısmı birleştir
            final_text = generated_prefix + " " + llm_text
            
            total_in += l_in
            total_out += l_out
            total_cost += l_cost
            
            inference_steps.append({
                "role": "llm_completion",
                "model_id": self.llm.model_id,
                "latency_ms": l_lat,
                "output_tokens": l_out,
                "cost_usd": l_cost
            })

        total_latency = (time.perf_counter() - t0) * 1000

        parsed = parse_answer(final_text, self.task_type)

        actual_confidence = sum(token_probs) / len(token_probs) if token_probs else 0.5
        return Response(
            query_id=query.id,
            text=final_text,
            predicted_answer=parsed,
            confidence=actual_confidence,
            model_id=self.llm.model_id if interrupted else self.slm.model_id,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "prompt_text": prompt,
                "slm_raw_text": generated_prefix,
                "slm_parsed_answer": parse_answer(generated_prefix, self.task_type),
                "final_raw_text": final_text,
                "final_parsed_answer": parsed,
                "final_answer_source": "llm" if interrupted else "slm",
                "confidence_threshold": self.threshold,
                "framework": "rtos_watchdog",
                "interrupted": interrupted,
                "streaming_error": streaming_error,
                "token_probs": token_probs,
                "slm_prefix": generated_prefix,
                "slm_tokens_before_interrupt": slm_tokens,
                "inference_steps": inference_steps,
            },
        )