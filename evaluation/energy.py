"""Energy and emissions tracking.

Two complementary sources:
  1. CodeCarbon v2.3.4 — software-level energy estimation (CPU + GPU + RAM)
  2. NVML (pynvml) — hardware-level instantaneous GPU power counter

Usage:
    tracker = EnergyTracker()
    tracker.start()
    # ... run inference ...
    reading = tracker.stop()
    print(reading.energy_kwh, reading.co2_g, reading.gpu_power_w)
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.types import Response


@dataclass
class EnergyReading:
    energy_kwh: float = 0.0
    co2_g: float = 0.0
    duration_s: float = 0.0
    gpu_power_w: float = 0.0
    tokens_per_kwh: float = 0.0


@dataclass(frozen=True)
class ResourceProfile:
    host_label: str
    hourly_usd: float
    gpu_power_w: float
    notes: str = ""


class EnergyTracker:
    """Wraps CodeCarbon + NVML. Gracefully degrades if neither is available."""

    def __init__(self, project_name: str = "thesis_benchmark", gpu_id: int = 0) -> None:
        self.project_name = project_name
        self.gpu_id = gpu_id
        self._cc_tracker = None
        self._nvml_handle = None
        self._t0: float = 0.0
        self._gpu_samples: list[float] = []
        self._sample_interval_s: float = 0.5

        self._init_codecarbon()
        self._init_nvml()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._t0 = time.perf_counter()
        self._gpu_samples = []
        if self._cc_tracker:
            try:
                self._cc_tracker.start()
            except Exception:
                self._cc_tracker = None

    def stop(self, total_tokens: int = 0) -> EnergyReading:
        duration_s = time.perf_counter() - self._t0
        energy_kwh = 0.0
        co2_g = 0.0

        if self._cc_tracker:
            try:
                emissions = self._cc_tracker.stop()
                co2_g = (emissions or 0.0) * 1000
                # Retrieve energy from the internal data
                data = getattr(self._cc_tracker, "_total_energy", None)
                if data is not None:
                    energy_kwh = float(data.kWh)
            except Exception:
                pass

        mean_gpu_w = float(sum(self._gpu_samples) / len(self._gpu_samples)) if self._gpu_samples else 0.0

        if energy_kwh == 0.0 and mean_gpu_w > 0.0:
            energy_kwh = mean_gpu_w * duration_s / 3600

        tokens_per_kwh = (total_tokens / energy_kwh) if (energy_kwh > 0 and total_tokens > 0) else 0.0

        return EnergyReading(
            energy_kwh=energy_kwh,
            co2_g=co2_g,
            duration_s=duration_s,
            gpu_power_w=mean_gpu_w,
            tokens_per_kwh=tokens_per_kwh,
        )

    def sample_gpu_power(self) -> float:
        """Read instantaneous GPU power in watts. Returns 0.0 on failure."""
        if self._nvml_handle is None:
            return 0.0
        try:
            import pynvml
            mw = pynvml.nvmlDeviceGetPowerUsage(self._nvml_handle)
            w = mw / 1000.0
            self._gpu_samples.append(w)
            return w
        except Exception:
            return 0.0

    # ------------------------------------------------------------------
    # Init helpers
    # ------------------------------------------------------------------

    def _init_codecarbon(self) -> None:
        try:
            from codecarbon import EmissionsTracker
            self._cc_tracker = EmissionsTracker(
                project_name=self.project_name,
                output_file="emissions.csv",
                log_level="error",
                save_to_file=True,
                gpu_ids=[self.gpu_id],
            )
        except ImportError:
            pass

    def _init_nvml(self) -> None:
        try:
            import pynvml
            pynvml.nvmlInit()
            self._nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(self.gpu_id)
        except Exception:
            self._nvml_handle = None


# ------------------------------------------------------------------
# Resource profile estimates for remote/self-hosted experiments
# ------------------------------------------------------------------

_DEFAULT_GRID_CO2_G_PER_KWH = 380.0

_DEFAULT_RESOURCE_PROFILES: dict[str, ResourceProfile] = {
    "gemma4-4b": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "google/gemma-4-E4B-it": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "qwen3.5-4b": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "Qwen/Qwen3.5-4B": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "llama3.2-3b": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "meta-llama/Llama-3.2-3B-Instruct": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "ministral3-3b": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "mistralai/Ministral-3-3B-Instruct-2512": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "phi4-mini": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "microsoft/Phi-4-mini-instruct": ResourceProfile("gcp-l4", 0.75, 72.0, "Single L4 host"),
    "gpt-oss-20b": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "openai/gpt-oss-20b": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "qwen3.5-27b": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "Qwen/Qwen3.5-27B": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "gemma4-31b": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "nvidia/Gemma-4-31B-IT-NVFP4": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "qwen3.5-35b-a3b": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "Qwen/Qwen3.5-35B-A3B": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "gemma4-26b-a4b": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "nvidia/Gemma-4-26B-A4B-NVFP4": ResourceProfile("gcp-g4-rtx6000", 2.35, 320.0, "Shared RTX PRO 6000 host"),
    "llama3.3-70b": ResourceProfile("nebius-h200", 6.50, 600.0, "Intended heavy host"),
    "meta-llama/Llama-3.3-70B-Instruct": ResourceProfile("nebius-h200", 6.50, 600.0, "Intended heavy host"),
    "gpt-oss-120b": ResourceProfile("nebius-h200", 6.50, 600.0, "Intended heavy host"),
    "openai/gpt-oss-120b": ResourceProfile("nebius-h200", 6.50, 600.0, "Intended heavy host"),
}

_MODEL_PARAMS: dict[str, float] = {
    "openai/gpt-oss-120b": 120e9,
    "meta-llama/Llama-3.3-70B-Instruct": 70e9,
    "Qwen/Qwen3.5-27B": 27e9,
    "openai/gpt-oss-20b": 20e9,
    "google/gemma-4-31B-it": 31e9,
    "google/gemma-4-26B-A4B-it": 3.8e9,
    "Qwen/Qwen3.5-35B-A3B": 3e9,
    "google/gemma-4-E4B-it": 4.5e9,
    "Qwen/Qwen3.5-4B": 4e9,
    "meta-llama/Llama-3.2-3B-Instruct": 3e9,
    "mistralai/Ministral-3-3B-Instruct-2512": 3e9,
    "microsoft/Phi-4-mini-instruct": 4e9,
}


def resolve_resource_profile(model_id: str) -> ResourceProfile | None:
    overrides = os.getenv("THESIS_MODEL_RESOURCE_OVERRIDES_JSON", "").strip()
    if overrides:
        try:
            payload = json.loads(overrides)
            if isinstance(payload, dict) and model_id in payload:
                item = payload[model_id]
                if isinstance(item, dict):
                    return ResourceProfile(
                        host_label=str(item.get("host_label", "custom")),
                        hourly_usd=float(item.get("hourly_usd", 0.0)),
                        gpu_power_w=float(item.get("gpu_power_w", 0.0)),
                        notes=str(item.get("notes", "override")),
                    )
        except Exception:
            pass
    return _DEFAULT_RESOURCE_PROFILES.get(model_id)


def estimate_step_usage(model_id: str, latency_ms: float) -> dict[str, float | str]:
    profile = resolve_resource_profile(model_id)
    duration_s = max(latency_ms, 0.0) / 1000.0
    if profile is None:
        return {
            "host_label": "unknown",
            "duration_s": duration_s,
            "energy_kwh": 0.0,
            "co2_g": 0.0,
            "infra_cost_usd": 0.0,
            "gpu_power_w": 0.0,
        }

    duration_h = duration_s / 3600.0
    energy_kwh = (profile.gpu_power_w / 1000.0) * duration_h
    grid_factor = float(os.getenv("THESIS_GRID_CO2_G_PER_KWH", _DEFAULT_GRID_CO2_G_PER_KWH))
    return {
        "host_label": profile.host_label,
        "duration_s": duration_s,
        "energy_kwh": energy_kwh,
        "co2_g": energy_kwh * grid_factor,
        "infra_cost_usd": profile.hourly_usd * duration_h,
        "gpu_power_w": profile.gpu_power_w,
    }


def annotate_response_resource_usage(response: Response) -> Response:
    steps = response.metadata.get("inference_steps")
    if not isinstance(steps, list) or not steps:
        steps = [
            {
                "role": "final",
                "model_id": response.model_id,
                "latency_ms": response.latency_ms,
                "api_cost_usd": response.cost_usd,
            }
        ]

    total_infra_cost = 0.0
    total_energy_kwh = 0.0
    total_co2_g = 0.0
    weighted_power = 0.0
    total_duration_s = 0.0
    enriched_steps: list[dict[str, float | str | bool | None]] = []

    for step in steps:
        if not isinstance(step, dict):
            continue
        model_id = str(step.get("model_id", "") or "")
        latency_ms = float(step.get("latency_ms", 0.0) or 0.0)
        usage = estimate_step_usage(model_id, latency_ms)
        total_infra_cost += float(usage["infra_cost_usd"])
        total_energy_kwh += float(usage["energy_kwh"])
        total_co2_g += float(usage["co2_g"])
        duration_s = float(usage["duration_s"])
        weighted_power += float(usage["gpu_power_w"]) * duration_s
        total_duration_s += duration_s
        enriched_steps.append({**step, **usage})

    response.api_cost_usd = response.cost_usd
    response.infra_cost_usd = total_infra_cost
    response.cost_usd = response.api_cost_usd + response.infra_cost_usd
    response.energy_kwh = total_energy_kwh
    response.co2_g = total_co2_g
    response.gpu_power_w = weighted_power / total_duration_s if total_duration_s > 0 else 0.0
    response.metadata["inference_steps"] = enriched_steps
    response.metadata["resource_estimate"] = {
        "api_cost_usd": response.api_cost_usd,
        "infra_cost_usd": response.infra_cost_usd,
        "total_cost_usd": response.cost_usd,
        "energy_kwh": response.energy_kwh,
        "co2_g": response.co2_g,
        "gpu_power_w": response.gpu_power_w,
        "method": "host_profile_estimate",
    }
    return response


# ------------------------------------------------------------------
# Convenience: Active Parameters per Token (AP/T)
# ------------------------------------------------------------------


def active_parameters_per_token(model_id: str, total_tokens: int) -> float:
    """AP/T = total active parameters / tokens generated.

    For dense models this equals model_params. For MoE selections we store
    active parameter counts so AP/T remains comparable across tiers.
    """
    params = _MODEL_PARAMS.get(model_id, 0.0)
    if total_tokens <= 0 or params == 0.0:
        return 0.0
    return params / total_tokens
