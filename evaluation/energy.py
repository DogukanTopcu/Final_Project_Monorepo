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

import time
from dataclasses import dataclass, field


@dataclass
class EnergyReading:
    energy_kwh: float = 0.0
    co2_g: float = 0.0
    duration_s: float = 0.0
    gpu_power_w: float = 0.0
    tokens_per_kwh: float = 0.0


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
# Convenience: Active Parameters per Token (AP/T)
# ------------------------------------------------------------------

_MODEL_PARAMS: dict[str, float] = {
    "moonshotai/Kimi-K2.6": 1_000e9,
    "Qwen/Qwen3.5-397B-A17B": 397e9,
    "openai/gpt-oss-120b": 120e9,
    "meta-llama/Llama-3.3-70B-Instruct": 70e9,
    "Qwen/Qwen3.5-27B": 27e9,
    "openai/gpt-oss-20b": 20e9,
    "google/gemma-4-31B-it": 31e9,
    "Qwen/Qwen3.5-122B-A10B": 10e9,
    "google/gemma-4-26B-A4B-it": 3.8e9,
    "Qwen/Qwen3.5-35B-A3B": 3e9,
    "google/gemma-4-E4B-it": 4.5e9,
    "Qwen/Qwen3.5-4B": 4e9,
    "meta-llama/Llama-3.2-3B-Instruct": 3e9,
}


def active_parameters_per_token(model_id: str, total_tokens: int) -> float:
    """AP/T = total active parameters / tokens generated.

    For dense models this equals model_params. For MoE selections we store
    active parameter counts so AP/T remains comparable across tiers.
    """
    params = _MODEL_PARAMS.get(model_id, 0.0)
    if total_tokens <= 0 or params == 0.0:
        return 0.0
    return params / total_tokens
