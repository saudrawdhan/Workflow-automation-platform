"""Executes a validated workflow graph and produces a run record."""
from __future__ import annotations

import time
import traceback
import uuid
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from .base import NODE_REGISTRY, NodeError
from .graph import topological_sort, validate


def _descendants(start: str, edges: List[Dict[str, Any]]) -> Set[str]:
    adjacency = defaultdict(list)
    for edge in edges:
        adjacency[edge["source"]].append(edge["target"])
    seen: Set[str] = set()
    stack = list(adjacency[start])
    while stack:
        node_id = stack.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        stack.extend(adjacency[node_id])
    return seen


def _gather_inputs(node_id: str, edges, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for edge in edges:
        if edge["target"] == node_id and edge["source"] in results:
            upstream = results[edge["source"]]
            if isinstance(upstream, dict):
                merged.update(upstream)
    return merged


def run(workflow: Dict[str, Any], run_id: Optional[str] = None) -> Dict[str, Any]:
    nodes = workflow.get("nodes", [])
    edges = workflow.get("edges", [])
    validate(nodes, edges)
    order = topological_sort(nodes, edges)
    by_id = {n["id"]: n for n in nodes}

    run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"
    started = time.time()
    results: Dict[str, Dict[str, Any]] = {}
    skipped: Set[str] = set()
    node_runs: List[Dict[str, Any]] = []
    overall = "success"

    for node_id in order:
        node = by_id[node_id]
        spec = NODE_REGISTRY[node["type"]]
        logs: List[str] = []
        record: Dict[str, Any] = {
            "node_id": node_id,
            "type": node["type"],
            "status": "pending",
            "output": None,
            "error": None,
            "ms": 0,
            "logs": logs,
        }

        if node_id in skipped:
            record["status"] = "skipped"
            node_runs.append(record)
            continue

        record["status"] = "running"
        clock = time.perf_counter()
        try:
            inputs = _gather_inputs(node_id, edges, results)
            produced = spec.execute(inputs, node.get("config") or {}, logs.append)
            produced = produced if isinstance(produced, dict) else {"value": produced}
            # Data accumulates along the path: downstream nodes see upstream context
            # plus what this node added. The record shows only what this node produced.
            results[node_id] = {**inputs, **produced}
            record["output"] = produced
            record["status"] = "success"
        except NodeError as exc:
            record["status"] = "error"
            record["error"] = str(exc)
            overall = "error"
            skipped |= _descendants(node_id, edges)
        except Exception as exc:  # contained: an unexpected failure never crashes the run
            record["status"] = "error"
            record["error"] = f"{type(exc).__name__}: {exc}"
            logs.append(traceback.format_exc().strip().splitlines()[-1])
            overall = "error"
            skipped |= _descendants(node_id, edges)
        finally:
            record["ms"] = round((time.perf_counter() - clock) * 1000, 1)

        node_runs.append(record)

    return {
        "run_id": run_id,
        "workflow_id": workflow.get("id"),
        "status": overall,
        "order": order,
        "started_at": started,
        "finished_at": time.time(),
        "node_runs": node_runs,
    }
