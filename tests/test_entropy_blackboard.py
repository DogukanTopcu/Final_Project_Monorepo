import os
import requests
from core.models import OpenAICompatibleModel, ModelProvider
from core.types import Query
from architectures.entropy_based_blackboard import DecentralizedBlackboardArchitecture

RUN_LOCAL = os.getenv("RUN_LOCAL_BLACKBOARD_TESTS") == "1"

SLM_PRIMARY_ID = os.getenv("BLACKBOARD_SLM_PRIMARY_ID", "qwen2.5:3b")
SLM_PRIMARY_URL = os.getenv("BLACKBOARD_SLM_PRIMARY_URL", "http://localhost:11434/v1")
SLM_SECONDARY_ID = os.getenv("BLACKBOARD_SLM_SECONDARY_ID", "llama3.2")
SLM_SECONDARY_URL = os.getenv("BLACKBOARD_SLM_SECONDARY_URL", "http://localhost:11434/v1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 1. Native Gemini API Provider (Bulletproof Token Handling)
class GeminiCloudProvider(ModelProvider):
    def __init__(self, api_key: str):
        super().__init__("gemini2.5-flash") # Safest native model name
        self.api_key = api_key
        # Call Google's native endpoint directly!
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"

    def generate(self, prompt: str, **kwargs):
        max_tokens = kwargs.get("max_tokens")
        
        # THE FIX: If bidding, use 5. If answering, use 800 native tokens!
        if not isinstance(max_tokens, int) or max_tokens > 5:
            max_tokens = 800
            
        payload = {
            "contents": [{"parts":[{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.1 
            }
        }
        
        try:
            resp = requests.post(self.url, json=payload, timeout=30)
            resp.raise_for_status() 
            
            data = resp.json()
            # Extract text using Google's native JSON structure
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            return text, 0.95, 0, 0, 0.0
            
        except Exception as e:
            print(f"\n[💥 API CRASH]: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[💥 GOOGLE'S ERROR MESSAGE]: {e.response.text}")
            return "API_CRASH_FALLBACK_TEXT", 0.0, 0, 0, 0.0


slm_primary = OpenAICompatibleModel(
    model_id=SLM_PRIMARY_ID,
    base_url=SLM_PRIMARY_URL,
)

slm_secondary = OpenAICompatibleModel(
    model_id=SLM_SECONDARY_ID,
    base_url=SLM_SECONDARY_URL,
)

llm_sweeper = GeminiCloudProvider(api_key=GEMINI_API_KEY or "")


def run_test():
    if not RUN_LOCAL:
        print("[SKIP] Set RUN_LOCAL_BLACKBOARD_TESTS=1 to run this local-only test.")
        return
    if not GEMINI_API_KEY:
        print("[SKIP] Set GEMINI_API_KEY to run this local-only test.")
        return
    print("\n🚀 Initializing ENTROPY-BASED Blackboard Swarm...")
    arch = DecentralizedBlackboardArchitecture(
        slm=slm_primary,
        secondary_slm=slm_secondary,
        llm=llm_sweeper,
        cost_weight=0.15,
        task_type="open"
    )

    query = Query(
        id="task_001",
        text="A boy has as many sisters as brothers, but each sister has only half as many sisters as brothers. How many brothers and sisters are there in the family?",
        choices=None
    )

    print(f"\n[USER QUERY]: {query.text}")
    print("-" * 60)
    
    response = arch.run(query)

    print("-" * 60)
    print(f"\n🎉 FINAL ANSWER:\n{response.text.strip()}\n")
    print(f"👑 Winning Model:  {response.model_id}")
    print(f"⏱️ Total Latency: {response.latency_ms:.2f} ms")
    
    print("\n[Inference Steps Log]:")
    for step in response.metadata["inference_steps"]:
        print(f" -> Worker: {step['worker']} | Latency: {step['latency_ms']:.2f}ms")

if __name__ == "__main__":
    run_test()