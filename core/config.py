from __future__ import annotations

import yaml
from pathlib import Path
from core.types import ExperimentConfig


def load_config(path: str | Path) -> ExperimentConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return ExperimentConfig(**{k: v for k, v in data.items() if k in ExperimentConfig.__dataclass_fields__})


def save_config(config: ExperimentConfig, path: str | Path) -> None:
    import dataclasses
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(dataclasses.asdict(config), f, default_flow_style=False)
