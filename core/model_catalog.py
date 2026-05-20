from __future__ import annotations

from dataclasses import dataclass
import json
import os


@dataclass(frozen=True)
class ModelSpec:
    id: str
    name: str
    family: str
    tier: str
    kind: str
    provider: str
    provider_model: str
    openai_compatible_model: str | None = None
    base_url_env: str | None = None
    base_url_default: str | None = None
    api_key_env: str | None = None


SELECTED_MODELS: tuple[ModelSpec, ...] = (
    ModelSpec(
        id="gpt-oss-120b",
        name="GPT OSS (120B)",
        family="GPT OSS",
        tier="heavy_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="openai/gpt-oss-120b",
        openai_compatible_model="openai/gpt-oss-120b",
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
        openai_compatible_model="meta-llama/Llama-3.3-70B-Instruct",
        base_url_env="VLLM_LLAMA33_70B_URL",
        base_url_default="http://localhost:8000/v1",
    ),
    ModelSpec(
        id="qwen3.5-27b",
        name="Qwen 3.5 (27B)",
        family="Qwen",
        tier="light_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="Qwen/Qwen3.5-27B",
        openai_compatible_model="Qwen/Qwen3.5-27B",
        base_url_env="VLLM_QWEN35_27B_URL",
        base_url_default="http://localhost:8004/v1",
    ),
    ModelSpec(
        id="gpt-oss-20b",
        name="GPT OSS (20B)",
        family="GPT OSS",
        tier="light_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="openai/gpt-oss-20b",
        openai_compatible_model="openai/gpt-oss-20b",
        base_url_env="VLLM_GPT_OSS_20B_URL",
        base_url_default="http://localhost:8005/v1",
    ),
    ModelSpec(
        id="gemma4-31b",
        name="Gemma 4 (31B)",
        family="Gemma",
        tier="light_llm",
        kind="llm",
        provider="openai_compatible",
        provider_model="nvidia/Gemma-4-31B-IT-NVFP4",
        openai_compatible_model="nvidia/Gemma-4-31B-IT-NVFP4",
        base_url_env="VLLM_GEMMA4_31B_URL",
        base_url_default="http://localhost:8006/v1",
    ),
    ModelSpec(
        id="gemma4-26b-a4b",
        name="Gemma 4 26B-A4B",
        family="Gemma",
        tier="moe",
        kind="llm",
        provider="openai_compatible",
        provider_model="nvidia/Gemma-4-26B-A4B-NVFP4",
        openai_compatible_model="nvidia/Gemma-4-26B-A4B-NVFP4",
        base_url_env="VLLM_GEMMA4_26B_A4B_URL",
        base_url_default="http://localhost:8008/v1",
    ),
    ModelSpec(
        id="qwen3.5-35b-a3b",
        name="Qwen 3.5 35B-A3B",
        family="Qwen",
        tier="moe",
        kind="llm",
        provider="openai_compatible",
        provider_model="Qwen/Qwen3.5-35B-A3B",
        openai_compatible_model="Qwen/Qwen3.5-35B-A3B",
        base_url_env="VLLM_QWEN35_35B_A3B_URL",
        base_url_default="http://localhost:8007/v1",
    ),
    ModelSpec(
        id="gemma4-4b",
        name="Gemma 4 (E4B)",
        family="Gemma",
        tier="slm",
        kind="slm",
        provider="openai_compatible",
        provider_model="google/gemma-4-E4B-it",
        openai_compatible_model="google/gemma-4-E4B-it",
        base_url_env="VLLM_GEMMA4_E4B_URL",
        base_url_default="http://localhost:8002/v1",
    ),
    ModelSpec(
        id="qwen3.5-4b",
        name="Qwen 3.5 (4B)",
        family="Qwen",
        tier="slm",
        kind="slm",
        provider="openai_compatible",
        provider_model="Qwen/Qwen3.5-4B",
        openai_compatible_model="Qwen/Qwen3.5-4B",
        base_url_env="VLLM_QWEN35_4B_URL",
        base_url_default="http://localhost:8001/v1",
    ),
    ModelSpec(
        id="llama3.2-3b",
        name="Llama 3.2 (3B)",
        family="Llama",
        tier="slm",
        kind="slm",
        provider="openai_compatible",
        provider_model="meta-llama/Llama-3.2-3B-Instruct",
        openai_compatible_model="meta-llama/Llama-3.2-3B-Instruct",
        base_url_env="VLLM_LLAMA32_3B_URL",
        base_url_default="http://localhost:8003/v1",
    ),
    ModelSpec(
        id="ministral3-3b",
        name="Ministral 3 (3B)",
        family="Ministral",
        tier="slm",
        kind="slm",
        provider="openai_compatible",
        provider_model="mistralai/Ministral-3-3B-Instruct-2512",
        openai_compatible_model="mistralai/Ministral-3-3B-Instruct-2512",
        base_url_env="VLLM_MINISTRAL3_3B_URL",
        base_url_default="http://localhost:8009/v1",
    ),
    ModelSpec(
        id="phi4-mini",
        name="Phi 4 Mini",
        family="Phi",
        tier="slm",
        kind="slm",
        provider="openai_compatible",
        provider_model="microsoft/Phi-4-mini-instruct",
        openai_compatible_model="microsoft/Phi-4-mini-instruct",
        base_url_env="VLLM_PHI4_MINI_URL",
        base_url_default="http://localhost:8010/v1",
    ),
)

MODEL_BY_ID: dict[str, ModelSpec] = {model.id: model for model in SELECTED_MODELS}
SLM_MODEL_IDS: tuple[str, ...] = tuple(model.id for model in SELECTED_MODELS if model.kind == "slm")
LLM_MODEL_IDS: tuple[str, ...] = tuple(model.id for model in SELECTED_MODELS if model.kind == "llm")


def get_model_spec(model_id: str) -> ModelSpec | None:
    return MODEL_BY_ID.get(model_id)


def _model_id_overrides() -> dict[str, str]:
    raw = os.getenv("THESIS_MODEL_ID_OVERRIDES", "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    overrides: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(key, str) and isinstance(value, str) and key.strip() and value.strip():
            overrides[key.strip()] = value.strip()
    return overrides


def get_served_model_id(model_id: str) -> str | None:
    overrides = _model_id_overrides()
    if model_id in overrides:
        return overrides[model_id]
    spec = get_model_spec(model_id)
    if spec is None:
        return None
    return spec.openai_compatible_model or spec.provider_model


def get_expected_runtime_model_ids(model_id: str) -> set[str]:
    spec = get_model_spec(model_id)
    if spec is None:
        return set()
    expected = {spec.provider_model}
    overrides = _model_id_overrides()
    if model_id in overrides:
        expected.add(overrides[model_id])
    if spec.openai_compatible_model:
        expected.add(spec.openai_compatible_model)
    return {item for item in expected if item}
