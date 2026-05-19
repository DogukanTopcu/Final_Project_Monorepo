"""Shared-host reservation and live status probing.

Two shared hosts can serve only one large model at a time: `rtx6000` and
`heavy`. Both use a process-wide `Lock` to serialize experiment runs and
optionally invoke a remote autoswitch script when the alias on disk does not
match the model the host is currently serving.
"""
from __future__ import annotations

from contextlib import nullcontext
import shlex
import shutil
import subprocess
from dataclasses import dataclass, field
from threading import Lock
import time
from typing import Callable

import requests

from core.hosts import HOSTS, HostSpec, base_url_for_host, get_host_for_model
from core.model_catalog import get_expected_runtime_model_ids, get_served_model_id
from core.models import get_model_runtime_status
from web.backend.dependencies import Settings


StatusCallback = Callable[[str, str], None]


@dataclass
class _HostLockState:
    lock: Lock = field(default_factory=Lock)
    holder: str | None = None


# host_id -> lock state
_LOCK_STATES: dict[str, _HostLockState] = {
    host.host_id: _HostLockState() for host in HOSTS if host.shared
}


def get_lock_state(host_id: str) -> _HostLockState | None:
    return _LOCK_STATES.get(host_id)


def list_shared_host_states() -> dict[str, _HostLockState]:
    return dict(_LOCK_STATES)


class SharedHostReservation:
    def __init__(
        self,
        model_id: str,
        host: HostSpec,
        settings: Settings,
        on_status: StatusCallback | None = None,
    ) -> None:
        self.model_id = model_id
        self.host = host
        self.settings = settings
        self.on_status = on_status
        self.state = _LOCK_STATES[host.host_id]
        self._acquired = False

    def __enter__(self) -> SharedHostReservation:
        self._emit(
            f"Waiting for shared {self.host.label} for {self.model_id}.",
            "shared_host_wait",
        )
        acquired = self.state.lock.acquire(timeout=self.settings.rtx6000_lock_timeout_s)
        if not acquired:
            raise RuntimeError(
                f"Timed out waiting for {self.host.label} lock after "
                f"{self.settings.rtx6000_lock_timeout_s} seconds."
            )

        self._acquired = True
        self.state.holder = self.model_id
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
            self.state.holder = None
            self.state.lock.release()
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
        probe_model_id = get_served_model_id(self.model_id)
        if not probe_model_id:
            raise RuntimeError(f"Could not resolve probe model id for {self.model_id}.")

        active_model_ids = fetch_served_model_ids(base_url)
        if active_model_ids & expected_model_ids:
            ready, reason = probe_chat_completions(base_url, probe_model_id)
            if ready:
                self._emit(
                    f"{self.host.label} already serves {self.model_id}.",
                    "shared_host_ready",
                )
                return
            self._emit(
                f"{self.host.label} reports {self.model_id}, but chat route is not ready yet: {reason}",
                "shared_host_wait",
            )

        # Only the RTX6000 host has an autoswitch script wired up; for others
        # we fail loudly so the operator can swap the container manually.
        if self.host.host_id != "rtx6000" or not self.settings.rtx6000_autoswitch_enabled:
            raise RuntimeError(
                f"{self.host.label} currently serves a different model; "
                f"please switch to {self.model_id} manually."
            )

        gcloud_path = shutil.which("gcloud")
        if gcloud_path is None:
            raise RuntimeError("gcloud CLI is not installed or not available on PATH.")

        self._emit(
            f"Switching {self.host.label} to {self.model_id}.",
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
                f"Failed to switch {self.host.label} to {self.model_id}: {stderr or exc}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Timed out while issuing switch command for {self.model_id}."
            ) from exc

        deadline = time.monotonic() + self.settings.rtx6000_switch_poll_timeout_s
        while time.monotonic() < deadline:
            active_model_ids = fetch_served_model_ids(base_url)
            if active_model_ids & expected_model_ids:
                ready, reason = probe_chat_completions(base_url, probe_model_id)
                if ready:
                    self._emit(
                        f"{self.host.label} is ready for {self.model_id}.",
                        "shared_host_ready",
                    )
                    return
                self._emit(
                    f"{self.host.label} switched to {self.model_id}, waiting for chat route: {reason}",
                    "shared_host_wait",
                )
            time.sleep(self.settings.rtx6000_poll_interval_s)

        raise RuntimeError(
            f"Timed out waiting for {self.host.label} to serve {self.model_id} "
            f"after {self.settings.rtx6000_switch_poll_timeout_s} seconds."
        )


def reserve_llm_host(
    model_id: str,
    settings: Settings,
    on_status: StatusCallback | None = None,
):
    if not model_id:
        return nullcontext()
    host = get_host_for_model(model_id)
    if host is None or not host.shared:
        return nullcontext()
    if host.host_id == "rtx6000" and not settings.rtx6000_autoswitch_enabled:
        return nullcontext()
    return SharedHostReservation(
        model_id=model_id, host=host, settings=settings, on_status=on_status
    )


def _expected_served_model_ids(model_id: str) -> set[str]:
    return get_expected_runtime_model_ids(model_id)


def fetch_served_model_ids(base_url: str) -> set[str]:
    """Public: probe an OpenAI-compatible host for its currently served model ids."""
    if not base_url:
        return set()
    try:
        response = requests.get(f"{base_url.rstrip('/')}/models", timeout=5.0)
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


def probe_chat_completions(base_url: str, model_id: str, timeout: float = 15.0) -> tuple[bool, str | None]:
    """Probe the OpenAI-compatible chat route with a tiny request."""
    if not base_url or not model_id:
        return False, "Missing base_url or model_id."

    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Ping"}],
        "temperature": 0,
        "max_tokens": 1,
    }
    try:
        response = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        return True, None
    except Exception as exc:
        return False, str(exc)


def probe_host(host: HostSpec) -> dict:
    """Return a snapshot of host status: reachability, active model, latency."""
    base_url = base_url_for_host(host)
    snapshot: dict = {
        "host_id": host.host_id,
        "label": host.label,
        "shared": host.shared,
        "configured_models": list(host.model_ids),
        "base_url": base_url,
        "is_reachable": False,
        "active_model_id": None,
        "active_served_ids": [],
        "last_probe_latency_ms": None,
        "notes": host.description,
    }
    if not base_url:
        snapshot["notes"] = "No base URL configured for any of this host's aliases."
        return snapshot

    t0 = time.perf_counter()
    served_ids = fetch_served_model_ids(base_url)
    latency_ms = (time.perf_counter() - t0) * 1000.0
    snapshot["last_probe_latency_ms"] = round(latency_ms, 2)
    snapshot["is_reachable"] = bool(served_ids)
    snapshot["active_served_ids"] = sorted(served_ids)

    # Map served ids back to the canonical alias we know about.
    for alias in host.model_ids:
        expected = _expected_served_model_ids(alias)
        if served_ids & expected:
            snapshot["active_model_id"] = alias
            break

    # Lock holder for shared hosts
    if host.shared:
        state = _LOCK_STATES.get(host.host_id)
        if state is not None:
            snapshot["locked"] = state.lock.locked()
            snapshot["lock_holder"] = state.holder
    return snapshot
