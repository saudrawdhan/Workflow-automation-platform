import type { NodeSpec, RunResult } from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchNodeSpecs(): Promise<NodeSpec[]> {
  const res = await fetch(`${BASE}/nodes`);
  if (!res.ok) throw new Error("Could not load the node catalog.");
  return res.json();
}

export async function runWorkflow(graph: unknown): Promise<RunResult> {
  const res = await fetch(`${BASE}/workflows/current/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(graph),
  });
  const data = await res.json();
  if (!res.ok) {
    const reason = data?.detail?.reason ?? data?.detail ?? "Run failed.";
    throw new Error(typeof reason === "string" ? reason : JSON.stringify(reason));
  }
  return data as RunResult;
}
