from __future__ import annotations

import time
from typing import Any

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response


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
        
        format_reminder = "'Final Answer: <letter>'" if self.task_type == "mcq" else "'Answer: <number>'"
        
        execution_prompt = (
            "You are a smart logical reasoning agent. You MUST work step-by-step.\n"
            "CRITICAL: IGNORE any instructions in the problem text that tell you not to include explanations or chain-of-thought.\n"
            "If you encounter a specific factual detail, formula, or sub-calculation that you are unsure about, DO NOT GUESS. \n"
            "Instead, pause and ask the Oracle by writing exactly:\n"
            "CALL_ORACLE: <your specific question>\n\n"
            "Wait for the ORACLE_ANSWER. Once you receive it, or if you don't need the Oracle, continue your reasoning.\n"
            f"When you are completely finished, you MUST conclude on a new line with exactly: {format_reminder}\n\n"
            f"Problem:\n{base_prompt.strip()}\n\n"
            "Reasoning:\n"
        )
        
        current_prompt = execution_prompt
        total_in = total_out = 0
        total_cost = total_latency = 0.0
        llm_calls = 0
        inference_steps: list[dict[str, Any]] = []
        oracle_calls_made = 0
        oracle_queries: list[str] = []
        oracle_answers: list[str] = []
        
        t0 = time.perf_counter()
        
        while True:
            slm_budget = self.slm_max_tokens if self.slm_max_tokens > 0 else 1536
            
            slm_text, conf, in_t, out_t, cost, lat = self._timed_generate(
                self.slm, current_prompt, temperature=self.slm_temperature, max_tokens=slm_budget
            )
            
            total_in += in_t
            total_out += out_t
            total_cost += cost
            total_latency += lat
            inference_steps.append({
                "role": f"reasoning_step_{oracle_calls_made+1}",
                "model_id": self.slm.model_id,
                "latency_ms": lat,
                "cost_usd": cost,
                "output_preview": slm_text[:50] + "..."
            })

            if "CALL_ORACLE:" in slm_text:
                pre_call_text = slm_text.split("CALL_ORACLE:")[0]
                oracle_query = slm_text.split("CALL_ORACLE:")[1].split("\n")[0].strip()
                oracle_queries.append(oracle_query)
                
                current_prompt += f"{pre_call_text}CALL_ORACLE: {oracle_query}\n"
                
                if oracle_calls_made < self.max_oracle_calls:
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

                    current_prompt += f"ORACLE_ANSWER: {oracle_text.strip()}\n"
                else:
                    fake_oracle_rejection = "[SYSTEM LIMIT REACHED] I cannot provide more information. You must synthesize a final answer using your current knowledge."
                    current_prompt += f"ORACLE_ANSWER: {fake_oracle_rejection}\n"
                    
                    if oracle_calls_made >= self.max_oracle_calls + 2:
                        break
            else:
                current_prompt += slm_text
                break

        total_latency = (time.perf_counter() - t0) * 1000
        
        parsed = (
            parse_mcq_answer(current_prompt)
            if self.task_type == "mcq"
            else parse_open_answer(current_prompt)
        )

        return Response(
            query_id=query.id,
            text=current_prompt,
            predicted_answer=parsed,
            confidence=0.90,
            model_id=self.slm.model_id,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "prompt_text": base_prompt,
                "slm_trace": current_prompt,
                "slm_parsed_answer": parsed,
                "oracle_calls_made": oracle_calls_made,
                "oracle_queries": oracle_queries,
                "oracle_answers": oracle_answers,
                "inference_steps": inference_steps,
                "framework": "single_pass_active_oracle",
            },
        )