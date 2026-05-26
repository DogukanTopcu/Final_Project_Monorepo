from __future__ import annotations

import time
from typing import Any

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response


# AŞAMA 1 PROMPTU: Modelin sadece bilgi toplaması ve Kahin'i kullanması için.
_INVESTIGATION_PROMPT = """You are an AI investigator. Your job is to gather information to solve the user's problem.
Think step-by-step. If you lack specific facts, formulas, or need a calculation, ask the Oracle by writing EXACTLY:
CALL_ORACLE: [your specific question]

Wait for the ORACLE_ANSWER. Once you have enough information to solve the problem definitively, write:
INVESTIGATION_COMPLETE
"""

_ORACLE_SYSTEM_PROMPT = """You are an absolute truth Oracle. 
You will be asked a very specific, narrow question by a smaller AI agent that is stuck.
Answer extremely concisely. Provide only the fact, formula, or calculation requested. Do not add conversational filler.
"""

class ActiveOracleArchitecture(BaseArchitecture):
    name = "active_oracle"

    def __init__(
        self,
        slm: ModelProvider,
        llm: ModelProvider,
        slm_temperature: float = 0.0,
        llm_temperature: float = 0.0,
        slm_max_tokens: int = 0,
        llm_max_tokens: int = 0,
        max_oracle_calls: int = 3,
        task_type: str = "mcq",
    ) -> None:
        super().__init__(slm, llm)
        self.slm_temperature = slm_temperature
        self.llm_temperature = llm_temperature
        self.slm_max_tokens = slm_max_tokens
        self.llm_max_tokens = llm_max_tokens
        self.max_oracle_calls = max_oracle_calls
        self.task_type = task_type

    def run(self, query: Query) -> Response:
        base_prompt = mcq_prompt(query) if self.task_type == "mcq" else open_prompt(query)
    
        investigation_trace = f"{_INVESTIGATION_PROMPT}\n\n[USER PROBLEM TO INVESTIGATE]\n{base_prompt}\n\nInvestigation Log:\n"
        
        total_in = total_out = 0
        total_cost = total_latency = 0.0
        llm_calls = 0
        inference_steps: list[dict[str, Any]] = []
        oracle_calls_made = 0
        oracle_queries: list[str] = []
        oracle_answers: list[str] = []
        
        t0 = time.perf_counter()
        
        while oracle_calls_made <= self.max_oracle_calls:
            slm_budget = self.slm_max_tokens if self.slm_max_tokens > 0 else 1024
            slm_text, conf, in_t, out_t, cost, lat = self._timed_generate(
                self.slm, investigation_trace, temperature=self.slm_temperature, max_tokens=slm_budget
            )
            total_in += in_t
            total_out += out_t
            total_cost += cost
            total_latency += lat
            inference_steps.append({
                "role": f"investigation_step_{oracle_calls_made+1}",
                "model_id": self.slm.model_id,
                "latency_ms": lat,
                "cost_usd": cost,
                "output_preview": slm_text[:50] + "..."
            })

            investigation_trace += f"{slm_text}\n"

            if "INVESTIGATION_COMPLETE" in slm_text:
                break

            if "CALL_ORACLE:" in slm_text:
                oracle_query = slm_text.split("CALL_ORACLE:")[1].split("\n")[0].strip()
                oracle_queries.append(oracle_query)
                
                oracle_prompt = f"{_ORACLE_SYSTEM_PROMPT}\n\nQuestion: {oracle_query}"
                oracle_budget = self.llm_max_tokens if self.llm_max_tokens > 0 else 256
                oracle_text, _, l_in, l_out, l_cost, l_lat = self._timed_generate(
                    self.llm, oracle_prompt, temperature=self.llm_temperature, max_tokens=oracle_budget
                )
                
                oracle_answers.append(oracle_text.strip())
                total_in += l_in
                total_out += l_out
                total_cost += l_cost
                total_latency += l_lat
                llm_calls += 1
                oracle_calls_made += 1
                
                inference_steps.append({
                    "role": f"oracle_response_{oracle_calls_made}",
                    "model_id": self.llm.model_id,
                    "latency_ms": l_lat,
                    "cost_usd": l_cost,
                    "oracle_query": oracle_query
                })

                investigation_trace += f"ORACLE_ANSWER: {oracle_text.strip()}\n"
            else:
                break

        final_generation_prompt = (
            f"You have conducted the following background investigation:\n"
            f"-----------------------------------\n"
            f"{investigation_trace}\n"
            f"-----------------------------------\n\n"
            f"Using the information above, complete the following user task strictly following their formatting rules:\n\n"
            f"[USER TASK]\n{base_prompt}"
        )
        
        slm_budget = self.slm_max_tokens if self.slm_max_tokens > 0 else 512
        final_text, final_conf, in_t, out_t, cost, lat = self._timed_generate(
            self.slm, final_generation_prompt, temperature=self.slm_temperature, max_tokens=slm_budget
        )
        
        total_in += in_t
        total_out += out_t
        total_cost += cost
        total_latency += lat
        
        inference_steps.append({
            "role": "final_formulation",
            "model_id": self.slm.model_id,
            "latency_ms": lat,
            "cost_usd": cost,
            "output_preview": final_text[:50] + "..."
        })

        total_latency = (time.perf_counter() - t0) * 1000
        
        parsed = (
            parse_mcq_answer(final_text)
            if self.task_type == "mcq"
            else parse_open_answer(final_text)
        )

        return Response(
            query_id=query.id,
            text=final_text,
            predicted_answer=parsed,
            confidence=final_conf,
            model_id=self.slm.model_id,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "prompt_text": base_prompt,
                "investigation_trace": investigation_trace,
                "slm_raw_text": final_text,
                "slm_parsed_answer": parsed,
                "oracle_calls_made": oracle_calls_made,
                "oracle_queries": oracle_queries,
                "oracle_answers": oracle_answers,
                "inference_steps": inference_steps,
                "framework": "active_oracle",
            },
        )