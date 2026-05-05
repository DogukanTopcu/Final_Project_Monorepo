from architectures.base import BaseArchitecture
from architectures.routing import RoutingArchitecture
from architectures.multi_agent import MultiAgentArchitecture
from architectures.ensemble import EnsembleArchitecture
from architectures.monolithic import MonolithicArchitecture
from architectures.multi_agent_crew import MultiAgentCrewArchitecture
from architectures.speculative_decoding import SpeculativeDecodingArchitecture


def get_architecture(name: str, **kwargs) -> BaseArchitecture:
    arch_map = {
        "routing":            RoutingArchitecture,
        "multi_agent":        MultiAgentArchitecture,
        "ensemble":           EnsembleArchitecture,
        "monolithic":         MonolithicArchitecture,
        "multi_agent_crew":   MultiAgentCrewArchitecture,
        "speculative":        SpeculativeDecodingArchitecture,
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
    "MonolithicArchitecture",
    "MultiAgentCrewArchitecture",
    "SpeculativeDecodingArchitecture",
    "get_architecture",
]
