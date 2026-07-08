"""Core node abstractions and the type registry the engine executes against."""
from __future__ import annotations

from typing import Any, Callable, Dict, List

Logger = Callable[[str], None]


class NodeError(Exception):
    """Raised by a node when its execution fails, carrying a user-facing message."""


class Node:
    """Base class every node type inherits. The engine only calls ``execute``."""

    type: str = ""
    display_name: str = ""
    category: str = "action"          # "source" | "action" | "sink"
    inputs: List[str] = ["in"]
    outputs: List[str] = ["out"]
    params_schema: Dict[str, Any] = {}

    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any], log: Logger) -> Dict[str, Any]:
        raise NotImplementedError

    def describe(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "display_name": self.display_name,
            "category": self.category,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "params_schema": self.params_schema,
        }


NODE_REGISTRY: Dict[str, Node] = {}


def register(cls):
    """Class decorator that instantiates a node type and adds it to the registry."""
    instance = cls()
    if not instance.type:
        raise ValueError(f"{cls.__name__} must define a non-empty 'type'")
    NODE_REGISTRY[instance.type] = instance
    return cls
