from architectures.active_oracle import ActiveOracleArchitecture
from architectures.base import BaseArchitecture
from architectures.blackboard import DecentralizedBlackboardArchitecture
from architectures.dynamic_bidding_architecture import DynamicBiddingArchitecture
from architectures.ensemble import EnsembleArchitecture
from architectures.entropy_based_blackboard import (
    DecentralizedBlackboardArchitecture as EntropyBlackboardArchitecture,
)
from architectures.monolithic import MonolithicArchitecture
from architectures.multi_agent import MultiAgentArchitecture
from architectures.multi_agent_crew import MultiAgentCrewArchitecture
from architectures.pure_swarm import PureSwarmArchitecture
from architectures.routing import RoutingArchitecture
from architectures.rtos_watchdog import RTOSWatchdogArchitecture
from architectures.speculative_decoding import SpeculativeDecodingArchitecture


def get_architecture(name: str, **kwargs) -> BaseArchitecture:
    arch_map = {
        "routing":            RoutingArchitecture,
        "multi_agent":        MultiAgentArchitecture,
        "ensemble":           EnsembleArchitecture,
        "active_oracle":      ActiveOracleArchitecture,
        "rtos_watchdog":      RTOSWatchdogArchitecture,
        "monolithic":         MonolithicArchitecture,
        "multi_agent_crew":   MultiAgentCrewArchitecture,
        "speculative":        SpeculativeDecodingArchitecture,
        "blackboard":         DecentralizedBlackboardArchitecture,
        "entropy_blackboard": EntropyBlackboardArchitecture,
        "pure_swarm":         PureSwarmArchitecture,
        "dynamic_bidding":    DynamicBiddingArchitecture,
    }
    cls = arch_map.get(name)
    if cls is None:
        raise ValueError(f"Unknown architecture: {name!r}. Choose from {list(arch_map)}")
    return cls(**kwargs)


__all__ = [
    "BaseArchitecture",
    "RoutingArchitecture",
    "MultiAgentArchitecture",
    "EnsembleArchitecture",
    "ActiveOracleArchitecture",
    "RTOSWatchdogArchitecture",
    "MonolithicArchitecture",
    "MultiAgentCrewArchitecture",
    "SpeculativeDecodingArchitecture",
    "DecentralizedBlackboardArchitecture",
    "EntropyBlackboardArchitecture",
    "PureSwarmArchitecture",
    "DynamicBiddingArchitecture",
    "get_architecture",
]
