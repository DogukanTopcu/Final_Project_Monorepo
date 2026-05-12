from __future__ import annotations

import argparse
import dataclasses
import json
from pathlib import Path
from typing import Any

from training.config import TrainingConfig, load_training_config
from training.registry import AdapterRecord, register_adapter


def _require_training_dependencies() -> dict[str, Any]:
    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig as PeftLoraConfig
        from peft import get_peft_model, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from transformers import BitsAndBytesConfig, DataCollatorForLanguageModeling
        from transformers import Trainer, TrainingArguments, set_seed
    except ImportError as exc:
        raise SystemExit(
            "Training dependencies are not installed. Install them with:\n"
            '  pip install -e ".[training]"\n'
            f"Original import error: {exc}"
        ) from exc

    return {
        "torch": torch,
        "load_dataset": load_dataset,
        "PeftLoraConfig": PeftLoraConfig,
        "get_peft_model": get_peft_model,
        "prepare_model_for_kbit_training": prepare_model_for_kbit_training,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
        "BitsAndBytesConfig": BitsAndBytesConfig,
        "DataCollatorForLanguageModeling": DataCollatorForLanguageModeling,
        "Trainer": Trainer,
        "TrainingArguments": TrainingArguments,
        "set_seed": set_seed,
    }


def _dtype_from_name(torch_module: Any, name: str):
    try:
        return getattr(torch_module, name)
    except AttributeError as exc:
        raise ValueError(f"Unsupported torch dtype: {name}") from exc


def _training_arguments(config: TrainingConfig, deps: dict[str, Any]):
    kwargs = {
        "output_dir": config.output_dir,
        "num_train_epochs": config.optimization.num_train_epochs,
        "max_steps": config.optimization.max_steps,
        "per_device_train_batch_size": config.optimization.per_device_train_batch_size,
        "per_device_eval_batch_size": config.optimization.per_device_eval_batch_size,
        "gradient_accumulation_steps": config.optimization.gradient_accumulation_steps,
        "learning_rate": config.optimization.learning_rate,
        "warmup_ratio": config.optimization.warmup_ratio,
        "weight_decay": config.optimization.weight_decay,
        "logging_steps": config.optimization.logging_steps,
        "save_steps": config.optimization.save_steps,
        "eval_steps": config.optimization.eval_steps,
        "save_total_limit": config.optimization.save_total_limit,
        "report_to": config.runtime.report_to,
        "seed": config.runtime.seed,
        "remove_unused_columns": False,
        "eval_strategy": config.optimization.eval_strategy,
    }
    try:
        return deps["TrainingArguments"](**kwargs)
    except TypeError:
        kwargs["evaluation_strategy"] = kwargs.pop("eval_strategy")
        return deps["TrainingArguments"](**kwargs)


def _load_json_dataset(config: TrainingConfig, deps: dict[str, Any]):
    data_files = {"train": config.dataset.train_file}
    if config.dataset.validation_file:
        data_files["validation"] = config.dataset.validation_file
    if config.dataset.test_file:
        data_files["test"] = config.dataset.test_file
    return deps["load_dataset"]("json", data_files=data_files)


def train(config: TrainingConfig, *, config_path: str | None = None) -> dict[str, Any]:
    deps = _require_training_dependencies()
    deps["set_seed"](config.runtime.seed)

    torch = deps["torch"]
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = deps["AutoTokenizer"].from_pretrained(
        config.base_model,
        trust_remote_code=config.runtime.trust_remote_code,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = None
    if config.quantization.load_in_4bit:
        quantization_config = deps["BitsAndBytesConfig"](
            load_in_4bit=True,
            bnb_4bit_compute_dtype=_dtype_from_name(
                torch, config.quantization.compute_dtype
            ),
            bnb_4bit_quant_type=config.quantization.quant_type,
            bnb_4bit_use_double_quant=config.quantization.double_quant,
        )

    model = deps["AutoModelForCausalLM"].from_pretrained(
        config.base_model,
        quantization_config=quantization_config,
        device_map=config.runtime.device_map,
        trust_remote_code=config.runtime.trust_remote_code,
    )
    if config.quantization.load_in_4bit:
        model = deps["prepare_model_for_kbit_training"](
            model,
            use_gradient_checkpointing=config.runtime.gradient_checkpointing,
        )
    elif config.runtime.gradient_checkpointing:
        model.gradient_checkpointing_enable()

    peft_config = deps["PeftLoraConfig"](
        r=config.lora.r,
        lora_alpha=config.lora.alpha,
        lora_dropout=config.lora.dropout,
        target_modules=config.lora.target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = deps["get_peft_model"](model, peft_config)

    raw_dataset = _load_json_dataset(config, deps)

    def tokenize_batch(batch: dict[str, list[str]]) -> dict[str, Any]:
        texts = batch[config.dataset.text_field]
        tokenized = tokenizer(
            texts,
            truncation=True,
            max_length=config.dataset.max_seq_length,
            padding=False,
        )
        tokenized["labels"] = [list(ids) for ids in tokenized["input_ids"]]
        return tokenized

    tokenized_dataset = raw_dataset.map(
        tokenize_batch,
        batched=True,
        remove_columns=raw_dataset["train"].column_names,
    )

    trainer = deps["Trainer"](
        model=model,
        args=_training_arguments(config, deps),
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset.get("validation"),
        data_collator=deps["DataCollatorForLanguageModeling"](
            tokenizer=tokenizer,
            mlm=False,
        ),
    )
    trainer.train()
    trainer.save_model(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)

    record = AdapterRecord(
        name=config.run_name,
        base_model=config.base_model,
        adapter_path=config.output_dir,
        domain=config.metadata.domain,
        task=config.metadata.task,
        source_dataset=config.metadata.source_dataset,
        training_config=config_path or "",
        notes=config.metadata.notes,
    )
    register_adapter(config.adapter_registry_path, record)

    summary = {
        "run_name": config.run_name,
        "base_model": config.base_model,
        "output_dir": config.output_dir,
        "adapter_registry_path": config.adapter_registry_path,
        "metadata": dataclasses.asdict(config.metadata),
    }
    with open(output_dir / "training_summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LoRA/QLoRA SFT training.")
    parser.add_argument("--config", required=True, help="Path to training YAML config.")
    args = parser.parse_args()

    config = load_training_config(args.config)
    summary = train(config, config_path=args.config)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

