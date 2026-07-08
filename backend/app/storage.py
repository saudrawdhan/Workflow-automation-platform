"""Filesystem persistence for workflows and run records (JSON, no external deps)."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA = Path(__file__).resolve().parent.parent / "data"
_WORKFLOWS = _DATA / "workflows"
_RUNS = _DATA / "runs"
for _directory in (_WORKFLOWS, _RUNS):
    _directory.mkdir(parents=True, exist_ok=True)


def save_workflow(workflow: Dict[str, Any]) -> Dict[str, Any]:
    workflow_id = workflow.get("id") or f"wf_{uuid.uuid4().hex[:8]}"
    workflow["id"] = workflow_id
    workflow.setdefault("created_at", time.time())
    (_WORKFLOWS / f"{workflow_id}.json").write_text(
        json.dumps(workflow, indent=2), encoding="utf-8"
    )
    return workflow


def list_workflows() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for path in sorted(_WORKFLOWS.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items.append({"id": data["id"], "name": data.get("name", data["id"])})
    return items


def get_workflow(workflow_id: str) -> Optional[Dict[str, Any]]:
    path = _WORKFLOWS / f"{workflow_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_run(run: Dict[str, Any]) -> Dict[str, Any]:
    (_RUNS / f"{run['run_id']}.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
    return run


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    path = _RUNS / f"{run_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
