from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    id: str
    name: str
    family: str
    tier: str
    kind: str
    provider: str
    provider_model: str
    base_url_env: str | None = None
    base_url_default: str | None = None
    api_key_env: str | None = None


SELECTED_MODELS: tuple[ModelSpec, ...] = (
    ModelSpec(
        id="kimi-k2.6-1t",
        name="Kimi K2.6 (1T)",
        family="Kimi",
        tier="heavy_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="moonshotai/Kimi-K2.6",
        base_url_env="VLLM_KIMI_K26_1T_URL",
        base_url_default="http://localhost:8010/v1",
        api_key_env="KIMI_API_KEY",
    ),
    ModelSpec(
        id="qwen3.5-397b-a17b",
        name="Qwen 3.5 (397B-A17B)",
        family="Qwen",
        tier="heavy_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="Qwen/Qwen3.5-397B-A17B",
        base_url_env="VLLM_QWEN35_397B_A17B_URL",
        base_url_default="http://localhost:8011/v1",
    ),
    ModelSpec(
        id="gpt-oss-120b",
        name="GPT OSS (120B)",
        family="GPT OSS",
        tier="heavy_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="openai/gpt-oss-120b",
        base_url_env="VLLM_GPT_OSS_120B_URL",
        base_url_default="http://localhost:8012/v1",
    ),
    ModelSpec(
        id="llama3.3-70b",
        name="Llama 3.3 (70B)",
        family="Llama",
        tier="heavy_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="meta-llama/Llama-3.3-70B-Instruct",
        base_url_env="VLLM_LLAMA33_70B_URL",
        base_url_default="http://localhost:8000/v1",
    ),
    ModelSpec(
        id="qwen3.5-27b",
        name="Qwen 3.5 (27B)",
        family="Qwen",
        tier="light_llm",
        kind="llm",
        provider="ollama",
        provider_model="qwen3.5:27b",
    ),
    ModelSpec(
        id="gpt-oss-20b",
        name="GPT OSS (20B)",
        family="GPT OSS",
        tier="light_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="openai/gpt-oss-20b",
        base_url_env="VLLM_GPT_OSS_20B_URL",
        base_url_default="http://localhost:8005/v1",
    ),
    ModelSpec(
        id="gemma4-31b",
        name="Gemma 4 (31B)",
        family="Gemma",
        tier="light_llm",
        kind="llm",
        provider="ollama",
        provider_model="gemma4:31b",
    ),
    ModelSpec(
        id="qwen3.5-122b-a10b",
        name="Qwen 3.5 122B-A10B",
        family="Qwen",
        tier="moe",
        kind="llm",
        provider="ollama",
        provider_model="qwen3.5:122b",
    ),
    ModelSpec(
        id="gemma4-26b-a4b",
        name="Gemma 4 26B-A4B",
        family="Gemma",
        tier="moe",
        kind="llm",
        provider="ollama",
        provider_model="gemma4:26b",
    ),
    ModelSpec(
        id="qwen3.5-35b-a3b",
        name="Qwen 3.5 35B-A3B",
        family="Qwen",
        tier="moe",
        kind="llm",
        provider="ollama",
        provider_model="qwen3.5:35b",
    ),
    ModelSpec(
        id="gemma4-4b",
        name="Gemma 4 (E4B)",
        family="Gemma",
        tier="slm",
        kind="slm",
        provider="ollama",
        provider_model="gemma4:e4b",
    ),
    ModelSpec(
        id="qwen3.5-4b",
        name="Qwen 3.5 (4B)",
        family="Qwen",
        tier="slm",
        kind="slm",
        provider="ollama",
        provider_model="qwen3.5:4b",
    ),
    ModelSpec(
        id="llama3.2-3b",
        name="Llama 3.2 (3B)",
        family="Llama",
        tier="slm",
        kind="slm",
        provider="ollama",
        provider_model="llama3.2:3b",
    ),
)

MODEL_BY_ID: dict[str, ModelSpec] = {model.id: model for model in SELECTED_MODELS}
SLM_MODEL_IDS: tuple[str, ...] = tuple(model.id for model in SELECTED_MODELS if model.kind == "slm")
LLM_MODEL_IDS: tuple[str, ...] = tuple(model.id for model in SELECTED_MODELS if model.kind == "llm")


def get_model_spec(model_id: str) -> ModelSpec | None:
    return MODEL_BY_ID.get(model_id)
