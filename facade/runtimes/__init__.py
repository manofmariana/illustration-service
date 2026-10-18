from .base import AgentError, AgentRuntime
from .dsh import DshRuntime
from .kimi import KimiRuntime

BACKENDS = {"kimi": KimiRuntime, "dsh": DshRuntime}


def make(name: str) -> AgentRuntime:
    return BACKENDS[name]()


__all__ = ["AgentError", "AgentRuntime", "BACKENDS", "DshRuntime", "KimiRuntime", "make"]
