import type { RunResult } from "../types";

const BADGE: Record<string, string> = {
  pending: "⚪",
  running: "🔵",
  success: "🟢",
  error: "🔴",
  skipped: "⚫",
};

export default function RunLog({ run }: { run: RunResult | null }) {
  return (
    <footer className="runlog">
      <strong>Run log</strong>
      {!run && <span className="muted"> — run a workflow to see per-node results.</span>}
      {run && <span className={`run-status ${run.status}`}> {run.status.toUpperCase()}</span>}
      <div className="runlog-items">
        {run?.node_runs.map((record) => (
          <span
            key={record.node_id}
            className="runlog-item"
            title={record.error ?? (record.logs ?? []).join("\n")}
          >
            {BADGE[record.status]} {record.node_id} · {record.type} · {record.ms}ms
            {record.error ? ` · ${record.error}` : ""}
          </span>
        ))}
      </div>
    </footer>
  );
}
