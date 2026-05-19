import os
from core.models import OpenAICompatibleModel
from core.types import Query
from architectures.blackboard import DecentralizedBlackboardArchitecture

os.environ["OPENAI_API_KEY"] = "AIzaSyAVDkdk_D1jrRg6tt1u5igGVeIAXo1egNo"

slm_primary = OpenAICompatibleModel(
    model_id="qwen2.5:3b", 
    base_url="http://localhost:11434/v1"
)

slm_secondary = OpenAICompatibleModel(
    model_id="llama3.2", 
    base_url="http://localhost:11434/v1"
)

llm_sweeper = OpenAICompatibleModel(
    model_id="gemini-2.5-flash", # Or "gemini-2.5-pro" for heavier reasoning
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def run_test():
    print("\n🚀 Initializing Decentralized Blackboard Swarm...")
    arch = DecentralizedBlackboardArchitecture(
        slm=slm_primary,
        secondary_slm=slm_secondary,
        llm=llm_sweeper,
        cost_weight=0.15,
        task_type="open" # Using open question for testing
    )

    # A tricky logic question to force the models to think
    query = Query(
        id="task_001",
        text="A boy has as many sisters as brothers, but each sister has only half as many sisters as brothers. How many brothers and sisters are there in the family?",
        choices=None
    )

    print(f"\n[USER QUERY]: {query.text}")
    print("-" * 60)
    
    # This triggers the async swarm
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