"""Catalog of architectures exposed to the frontend.

Returns a structured spec for each architecture (mode, required models,
tunable parameters) so the UI can render a self-describing form.
"""
from __future__ import annotations

from fastapi import APIRouter

from web.backend.schemas import (
    Architecture,
    ArchitectureMode,
    ArchitectureParamSpec,
    ArchitectureSpec,
)

router = APIRouter(prefix="/architectures", tags=["architectures"])


def _temp_params() -> list[ArchitectureParamSpec]:
    return [
        ArchitectureParamSpec(
            key="slm_temperature",
            label="SLM temperature",
            type="float",
            default=0.0,
            min=0.0,
            max=2.0,
            description="Sampling temperature for SLM calls.",
        ),
        ArchitectureParamSpec(
            key="llm_temperature",
            label="LLM temperature",
            type="float",
            default=0.0,
            min=0.0,
            max=2.0,
            description="Sampling temperature for LLM calls.",
        ),
        ArchitectureParamSpec(
            key="slm_max_tokens",
            label="SLM max tokens",
            type="int",
            default=2000,
            min=0,
            max=32768,
            description="0 = auto budget.",
        ),
        ArchitectureParamSpec(
            key="llm_max_tokens",
            label="LLM max tokens",
            type="int",
            default=2000,
            min=0,
            max=32768,
            description="0 = auto budget.",
        ),
    ]


def _slm_params() -> list[ArchitectureParamSpec]:
    return [
        ArchitectureParamSpec(
            key="slm_temperature",
            label="SLM temperature",
            type="float",
            default=0.0,
            min=0.0,
            max=2.0,
            description="Sampling temperature for SLM calls.",
        ),
        ArchitectureParamSpec(
            key="slm_max_tokens",
            label="SLM max tokens",
            type="int",
            default=2000,
            min=0,
            max=32768,
            description="0 = auto budget.",
        ),
    ]


def _max_subtasks_param() -> ArchitectureParamSpec:
    return ArchitectureParamSpec(
        key="max_subtasks",
        label="Max sub-tasks limit",
        type="int",
        default=2,
        min=0,
        max=5,
        description="Maximum sub-tasks spawned and nesting depth allowed to prevent infinite loops.",
    )


_SPECS: list[ArchitectureSpec] = [
    ArchitectureSpec(
        id=Architecture.MONOLITHIC,
        name="Monolithic",
        mode=ArchitectureMode.MONOLITHIC,
        description="Single LLM answers every query directly. Accuracy/cost ceiling baseline.",
        requires_slm=False,
        requires_llm=True,
        params=[
            ArchitectureParamSpec(
                key="llm_temperature",
                label="Temperature",
                type="float",
                default=0.0,
                min=0.0,
                max=2.0,
            ),
            ArchitectureParamSpec(
                key="llm_max_tokens",
                label="Max tokens",
                type="int",
                default=2000,
                min=0,
                max=32768,
                description="0 = auto budget.",
            ),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.ROUTING,
        name="Routing (SLM → LLM)",
        mode=ArchitectureMode.HYBRID,
        description="SLM drafts an answer; low-confidence cases escalate to the LLM.",
        requires_slm=True,
        requires_llm=True,
        params=[
            ArchitectureParamSpec(
                key="confidence_threshold",
                label="Escalation threshold",
                type="float",
                default=0.7,
                min=0.0,
                max=1.0,
                description="Escalate to LLM if SLM confidence is below this value.",
            ),
            *_temp_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.MULTI_AGENT,
        name="Multi-Agent Debate",
        mode=ArchitectureMode.HYBRID,
        description="Proponent / opponent / arbitrator debate flow across SLM and LLM.",
        requires_slm=True,
        requires_llm=True,
        params=[
            ArchitectureParamSpec(
                key="arbitrator",
                label="Arbitrator",
                type="enum",
                default="llm",
                options=["slm", "llm"],
            ),
            ArchitectureParamSpec(
                key="n_debate_rounds",
                label="Debate rounds",
                type="int",
                default=1,
                min=1,
                max=5,
            ),
            *_temp_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.ACTIVE_ORACLE,
        name="Active Oracle",
        mode=ArchitectureMode.HYBRID,
        description="SLM reasons step-by-step and queries a truth oracle (LLM) when stuck.",
        requires_slm=True,
        requires_llm=True,
        params=[
            ArchitectureParamSpec(
                key="max_oracle_calls",
                label="Max oracle calls",
                type="int",
                default=3,
                min=0,
                max=10,
                description="Upper bound on oracle queries per sample.",
            ),
            *_temp_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.RTOS_WATCHDOG,
        name="RTOS Watchdog",
        mode=ArchitectureMode.HYBRID,
        description="Stream SLM tokens and interrupt to LLM when confidence drops.",
        requires_slm=True,
        requires_llm=True,
        params=[
            ArchitectureParamSpec(
                key="confidence_threshold",
                label="Interrupt threshold",
                type="float",
                default=0.6,
                min=0.0,
                max=1.0,
                description="Interrupt when token probability drops below this value.",
            ),
            ArchitectureParamSpec(
                key="slm_url",
                label="SLM Stream URL",
                type="string",
                default="auto",
                description="Use 'auto' to infer from backend model config, or provide a URL.",
            ),
            *_temp_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.ENSEMBLE,
        name="SLM Ensemble (voting)",
        mode=ArchitectureMode.ENSEMBLE,
        description="Multiple SLMs vote; optional LLM tiebreak.",
        requires_slm=True,
        requires_llm=False,
        supports_multi_slm=True,
        params=[
            ArchitectureParamSpec(
                key="n_models",
                label="Ensemble size",
                type="int",
                default=3,
                min=2,
                max=8,
                description="Auto-set to the number of SLMs you pick.",
            ),
            ArchitectureParamSpec(
                key="voting",
                label="Voting",
                type="enum",
                default="majority",
                options=["majority", "weighted"],
            ),
            ArchitectureParamSpec(
                key="llm_tiebreak",
                label="LLM tiebreak",
                type="bool",
                default=False,
                description="Call LLM only when no majority emerges.",
            ),
            *_temp_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.MULTI_AGENT_CREW,
        name="Multi-Agent Crew (experimental)",
        mode=ArchitectureMode.ENSEMBLE,
        description="Domain-routed crew of 3 specialist SLMs (reasoning / code / factual).",
        requires_slm=False,
        requires_llm=False,
        experimental=True,
        params=[],
    ),
    ArchitectureSpec(
        id=Architecture.SPECULATIVE,
        name="Speculative Decoding (experimental)",
        mode=ArchitectureMode.HYBRID,
        description="Drafter SLM proposes tokens; verifier LLM accepts or rewrites.",
        requires_slm=True,
        requires_llm=True,
        experimental=True,
        params=[
            ArchitectureParamSpec(
                key="speculative_acceptance_threshold",
                label="Acceptance threshold",
                type="float",
                default=0.7,
                min=0.0,
                max=1.0,
                description="Accept the draft when mean acceptance ≥ threshold.",
            ),
            *_temp_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.BLACKBOARD,
        name="Decentralized Blackboard",
        mode=ArchitectureMode.SWARM,
        description=(
            "Event-driven bossless SLM swarm. Two SLMs bid on tasks autonomously; "
            "the 70B model wakes only when a task stalls past its TTL."
        ),
        requires_slm=True,
        requires_llm=True,
        requires_secondary_slm=True,
        params=[
            ArchitectureParamSpec(
                key="cost_weight",
                label="Cost weight",
                type="float",
                default=0.15,
                min=0.0,
                max=1.0,
                description="Higher → swarm avoids the heavy sweeper longer.",
            ),
            ArchitectureParamSpec(
                key="bid_threshold",
                label="Bid threshold",
                type="float",
                default=0.65,
                min=0.0,
                max=1.0,
                description="Minimum bid needed before a worker claims a task.",
            ),
            ArchitectureParamSpec(
                key="ttl_ms",
                label="Task TTL (ms)",
                type="int",
                default=1500,
                min=100,
                max=10000,
                description="After TTL, the heavy sweeper can claim the task.",
            ),
            _max_subtasks_param(),
            *_temp_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.ENTROPY_BLACKBOARD,
        name="Entropy Blackboard",
        mode=ArchitectureMode.SWARM,
        description="Bossless swarm with entropy-based bidding and heavy sweeper fallback.",
        requires_slm=True,
        requires_llm=True,
        requires_secondary_slm=True,
        params=[
            ArchitectureParamSpec(
                key="cost_weight",
                label="Cost weight",
                type="float",
                default=0.15,
                min=0.0,
                max=1.0,
                description="Higher → swarm avoids the heavy sweeper longer.",
            ),
            ArchitectureParamSpec(
                key="bid_threshold",
                label="Bid threshold",
                type="float",
                default=0.65,
                min=0.0,
                max=1.0,
                description="Minimum bid needed before a worker claims a task.",
            ),
            ArchitectureParamSpec(
                key="ttl_ms",
                label="Task TTL (ms)",
                type="int",
                default=1500,
                min=100,
                max=10000,
                description="After TTL, the heavy sweeper can claim the task.",
            ),
            _max_subtasks_param(),
            *_temp_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.PURE_SWARM,
        name="Pure Swarm",
        mode=ArchitectureMode.SWARM,
        description="Bossless peer-to-peer SLM swarm without an LLM fallback.",
        requires_slm=True,
        requires_llm=False,
        requires_secondary_slm=True,
        params=[
            ArchitectureParamSpec(
                key="cost_weight",
                label="Cost weight",
                type="float",
                default=0.15,
                min=0.0,
                max=1.0,
                description="Higher → penalizes bids from smaller models.",
            ),
            ArchitectureParamSpec(
                key="bid_threshold",
                label="Bid threshold",
                type="float",
                default=0.65,
                min=0.0,
                max=1.0,
                description="Minimum bid needed before a peer claims the task.",
            ),
            ArchitectureParamSpec(
                key="ttl_ms",
                label="Task TTL (ms)",
                type="int",
                default=1500,
                min=100,
                max=10000,
                description="After TTL, the bid threshold drops to 0.",
            ),
            _max_subtasks_param(),
            ArchitectureParamSpec(
                key="allow_nested_subtasks",
                label="Allow nested sub-tasks",
                type="bool",
                default=False,
                description="Allows sub-tasks to spawn their own nested sub-tasks (sub-task of sub-task).",
            ),
            *_slm_params(),
        ],
    ),
    ArchitectureSpec(
        id=Architecture.DYNAMIC_BIDDING,
        name="Dynamic Bidding",
        mode=ArchitectureMode.SWARM,
        description="Zero-shot bidding swarm across a dynamic list of SLMs.",
        requires_slm=True,
        requires_llm=False,
        supports_multi_slm=True,
        params=[
            ArchitectureParamSpec(
                key="cost_weight",
                label="Cost weight",
                type="float",
                default=0.15,
                min=0.0,
                max=1.0,
                description="Higher → penalizes bids from more expensive models.",
            ),
            ArchitectureParamSpec(
                key="initial_bid_threshold",
                label="Initial bid threshold",
                type="float",
                default=0.95,
                min=0.0,
                max=1.0,
            ),
            ArchitectureParamSpec(
                key="min_bid_threshold",
                label="Min bid threshold",
                type="float",
                default=0.0,
                min=0.0,
                max=1.0,
            ),
            ArchitectureParamSpec(
                key="ttl_ms",
                label="Task TTL (ms)",
                type="int",
                default=1500,
                min=100,
                max=10000,
            ),
            *_slm_params(),
        ],
    ),
]


@router.get("", response_model=list[ArchitectureSpec])
def list_architectures() -> list[ArchitectureSpec]:
    return _SPECS
