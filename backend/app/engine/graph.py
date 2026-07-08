"""Graph validation and topological ordering (Kahn's algorithm)."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List, Tuple

from .base import NODE_REGISTRY


class ValidationError(Exception):
    """Raised before execution when a workflow is structurally invalid."""


class CycleError(ValidationError):
    """Raised when the workflow graph contains a cycle."""


def _index(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for node in nodes:
        nid = node.get("id")
        if not nid:
            raise ValidationError("Every node needs an 'id'.")
        if nid in by_id:
            raise ValidationError(f"Duplicate node id: {nid}")
        by_id[nid] = node
    return by_id


def _degrees(nodes, edges) -> Tuple[Dict[str, int], Dict[str, int]]:
    in_degree = {n["id"]: 0 for n in nodes}
    out_degree = {n["id"]: 0 for n in nodes}
    for edge in edges:
        out_degree[edge["source"]] += 1
        in_degree[edge["target"]] += 1
    return in_degree, out_degree


def validate(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> None:
    if not nodes:
        raise ValidationError("Workflow has no nodes.")
    by_id = _index(nodes)

    for node in nodes:
        ntype = node.get("type")
        if ntype not in NODE_REGISTRY:
            raise ValidationError(f"Unknown node type: {ntype!r}")
        spec = NODE_REGISTRY[ntype]
        config = node.get("config") or {}
        for name, schema in spec.params_schema.items():
            if schema.get("required") and not config.get(name):
                raise ValidationError(
                    f"{spec.display_name} ({node['id']}): missing required '{name}'."
                )

    for edge in edges:
        if edge.get("source") not in by_id:
            raise ValidationError(f"Edge references unknown source: {edge.get('source')}")
        if edge.get("target") not in by_id:
            raise ValidationError(f"Edge references unknown target: {edge.get('target')}")

    in_degree, out_degree = _degrees(nodes, edges)
    if not any(d == 0 for d in in_degree.values()):
        raise ValidationError("Workflow needs at least one start node (no incoming edges).")
    if not any(d == 0 for d in out_degree.values()):
        raise ValidationError("Workflow needs at least one end node (no outgoing edges).")

    topological_sort(nodes, edges)


def topological_sort(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
    in_degree = {n["id"]: 0 for n in nodes}
    adjacency = defaultdict(list)
    for edge in edges:
        adjacency[edge["source"]].append(edge["target"])
        in_degree[edge["target"]] += 1

    queue = deque(nid for nid, degree in in_degree.items() if degree == 0)
    order: List[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for nxt in adjacency[nid]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)

    if len(order) != len(nodes):
        stuck = [n["id"] for n in nodes if n["id"] not in set(order)]
        raise CycleError(f"Workflow has a cycle involving: {', '.join(stuck)}")
    return order
