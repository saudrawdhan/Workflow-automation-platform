"""FastAPI application exposing the workflow builder's REST API."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import storage
from .engine import NODE_REGISTRY, run
from .engine.graph import ValidationError

app = FastAPI(title="Nexta Flow", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

_UPLOADS = Path(__file__).resolve().parent.parent / "data" / "uploads"
_UPLOADS.mkdir(parents=True, exist_ok=True)


@app.get("/nodes")
def list_nodes():
    return [spec.describe() for spec in NODE_REGISTRY.values()]


@app.get("/workflows")
def get_workflows():
    return storage.list_workflows()


@app.post("/workflows")
def create_workflow(workflow: dict):
    return storage.save_workflow(workflow)


@app.get("/workflows/{workflow_id}")
def read_workflow(workflow_id: str):
    workflow = storage.get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return workflow


@app.post("/workflows/{workflow_id}/run")
def run_workflow(workflow_id: str, workflow: Optional[dict] = None):
    graph = workflow or storage.get_workflow(workflow_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    graph.setdefault("id", workflow_id)
    try:
        result = run(graph)
    except ValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_workflow", "reason": str(exc)},
        )
    storage.save_run(result)
    return result


@app.get("/runs/{run_id}")
def read_run(run_id: str):
    record = storage.get_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return record


@app.post("/upload")
async def upload_file(file: UploadFile):
    token = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    destination = _UPLOADS / token
    with destination.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return {"path": str(destination), "filename": file.filename}
