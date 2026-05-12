from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DatasetConfig:
    train_file: str
    validation_file: str | None = None
    test_file: str | None = None
    text_field: str = "text"
    max_seq_length: int = 2048


@dataclass
class LoraConfig:
    r: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: list[str] = field(
        default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj"]
    )


@dataclass
class QuantizationConfig:
    load_in_4bit: bool = True
    compute_dtype: str = "bfloat16"
    quant_type: str = "nf4"
    double_quant: bool = True


@dataclass
class OptimizationConfig:
    num_train_epochs: float = 1.0
    max_steps: int = -1
    per_device_train_batch_size: int = 1
    per_device_eval_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    weight_decay: float = 0.0
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 100
    eval_strategy: str = "steps"
    save_total_limit: int = 2


@dataclass
class RuntimeConfig:
    seed: int = 42
    device_map: str = "auto"
    trust_remote_code: bool = True
    gradient_checkpointing: bool = True
    report_to: list[str] = field(default_factory=lambda: ["none"])


@dataclass
class AdapterMetadata:
    domain: str = "coding"
    task: str = "sft"
    source_dataset: str = ""
    intended_use: str = "ablation"
    notes: str = ""


@dataclass
class TrainingConfig:
    run_name: str
    base_model: str
    output_dir: str
    dataset: DatasetConfig
    lora: LoraConfig = field(default_factory=LoraConfig)
    quantization: QuantizationConfig = field(default_factory=QuantizationConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    metadata: AdapterMetadata = field(default_factory=AdapterMetadata)
    adapter_registry_path: str = "training/adapters/registry.json"


def _build_dataclass(cls: type, data: dict[str, Any]):
    allowed = {f.name for f in fields(cls)}
    unknown = sorted(set(data) - allowed)
    if unknown:
        joined = ", ".join(unknown)
        raise ValueError(f"Unknown keys for {cls.__name__}: {joined}")
    return cls(**data)


def training_config_from_dict(data: dict[str, Any]) -> TrainingConfig:
    payload = dict(data)
    payload["dataset"] = _build_dataclass(DatasetConfig, payload.get("dataset", {}))

    if "lora" in payload:
        payload["lora"] = _build_dataclass(LoraConfig, payload["lora"])
    if "quantization" in payload:
        payload["quantization"] = _build_dataclass(
            QuantizationConfig, payload["quantization"]
        )
    if "optimization" in payload:
        payload["optimization"] = _build_dataclass(
            OptimizationConfig, payload["optimization"]
        )
    if "runtime" in payload:
        payload["runtime"] = _build_dataclass(RuntimeConfig, payload["runtime"])
    if "metadata" in payload:
        payload["metadata"] = _build_dataclass(AdapterMetadata, payload["metadata"])

    return _build_dataclass(TrainingConfig, payload)


def load_training_config(path: str | Path) -> TrainingConfig:
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return training_config_from_dict(data)

