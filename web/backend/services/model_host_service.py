from __future__ import annotations

from contextlib import nullcontext
import shlex
import shutil
import subprocess
from threading import Lock
import time
from typing import Callable

import requests

from core.model_catalog import get_model_spec
from core.models import get_model_runtime_status
from web.backend.dependencies import Settings


StatusCallback = Callable[[str, str], None]

_RTX6000_MODEL_IDS = {
    "gpt-oss-20b",
    "qwen3.5-27b",
    "gemma4-31b",
    "qwen3.5-35b-a3b",
    "gemma4-26b-a4b",
    "qwen3.5-122b-a10b",
}
_RTX6000_HOST_LOCK = Lock()


class SharedHostReservation:
    def __init__(self, model_id: str, settings: Settings, on_status: StatusCallback | None = None) -> None:
        self.model_id = model_id
        self.settings = settings
        self.on_status = on_status
        self._lock = _RTX6000_HOST_LOCK
        self._acquired = False

    def __enter__(self) -> SharedHostReservation:
        self._emit(
            f"Waiting for shared RTX6000 host for {self.model_id}.",
            "shared_host_wait",
        )
        acquired = self._lock.acquire(timeout=self.settings.rtx6000_lock_timeout_s)
        if not acquired:
            raise RuntimeError(
                f"Timed out waiting for shared RTX6000 host lock after "
                f"{self.settings.rtx6000_lock_timeout_s} seconds."
            )

        self._acquired = True
        try:
            self._ensure_model_active()
        except Exception:
            self._release()
            raise
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._release()

    def _release(self) -> None:
        if self._acquired:
            self._lock.release()
            self._acquired = False

    def _emit(self, message: str, status: str) -> None:
        if self.on_status is not None:
            self.on_status(message, status)

    def _ensure_model_active(self) -> None:
        runtime = get_model_runtime_status(self.model_id)
        if not bool(runtime.get("available")):
            raise RuntimeError(str(runtime.get("reason", f"{self.model_id} is unavailable.")))

        base_url = str(runtime.get("base_url", "")).rstrip("/")
        expected_model_ids = _expected_served_model_ids(self.model_id)
        if not expected_model_ids:
            raise RuntimeError(f"Could not resolve served model ids for {self.model_id}.")

        active_model_ids = _fetch_served_model_ids(base_url)
        if active_model_ids & expected_model_ids:
            self._emit(
                f"Shared RTX6000 host already serves {self.model_id}.",
                "shared_host_ready",
            )
            return

        gcloud_path = shutil.which("gcloud")
        if gcloud_path is None:
            raise RuntimeError("gcloud CLI is not installed or not available on PATH.")

        self._emit(
            f"Switching shared RTX6000 host to {self.model_id}.",
            "shared_host_switching",
        )
        remote_cmd = f"{self.settings.rtx6000_switch_script} {shlex.quote(self.model_id)}"
        cmd = [
            gcloud_path,
            "compute",
            "ssh",
            self.settings.rtx6000_instance_name,
            f"--project={self.settings.rtx6000_project}",
            f"--zone={self.settings.rtx6000_zone}",
            "--command",
            f"bash -lc {shlex.quote(remote_cmd)}",
        ]
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=self.settings.rtx6000_switch_command_timeout_s,
            )
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            raise RuntimeError(
                f"Failed to switch RTX6000 host to {self.model_id}: {stderr or exc}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Timed out while issuing RTX6000 switch command for {self.model_id}."
            ) from exc

        deadline = time.monotonic() + self.settings.rtx6000_switch_poll_timeout_s
        while time.monotonic() < deadline:
            active_model_ids = _fetch_served_model_ids(base_url)
            if active_model_ids & expected_model_ids:
                self._emit(
                    f"Shared RTX6000 host is ready for {self.model_id}.",
                    "shared_host_ready",
                )
                return
            time.sleep(self.settings.rtx6000_poll_interval_s)

        raise RuntimeError(
            f"Timed out waiting for shared RTX6000 host to serve {self.model_id} "
            f"after {self.settings.rtx6000_switch_poll_timeout_s} seconds."
        )


def reserve_llm_host(
    model_id: str,
    settings: Settings,
    on_status: StatusCallback | None = None,
):
    if not settings.rtx6000_autoswitch_enabled:
        return nullcontext()
    if model_id not in _RTX6000_MODEL_IDS:
        return nullcontext()
    return SharedHostReservation(model_id=model_id, settings=settings, on_status=on_status)


def _expected_served_model_ids(model_id: str) -> set[str]:
    spec = get_model_spec(model_id)
    if spec is None:
        return set()
    expected = {spec.provider_model}
    if spec.openai_compatible_model:
        expected.add(spec.openai_compatible_model)
    return {item for item in expected if item}


def _fetch_served_model_ids(base_url: str) -> set[str]:
    try:
        response = requests.get(f"{base_url}/models", timeout=5.0)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return set()

    data = payload.get("data", [])
    if not isinstance(data, list):
        return set()

    model_ids: set[str] = set()
    for item in data:
        if not isinstance(item, dict):
            continue
        model_id = item.get("id")
        if isinstance(model_id, str) and model_id.strip():
            model_ids.add(model_id.strip())
    return model_ids
