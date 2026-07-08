import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { WFData } from "../types";

const BADGE: Record<string, string> = {
  pending: "○",
  running: "◐",
  success: "✓",
  error: "✕",
  skipped: "–",
};

export default function WorkflowNode({ data }: NodeProps) {
  const node = data as WFData;
  const status = node.status ?? "pending";
  const out = node.output;

  let preview = "";
  if (out) {
    if (out.label) {
      const pct = typeof out.confidence === "number" ? `  ·  ${Math.round(out.confidence * 100)}%` : "";
      preview = `${out.label}${pct}`;
    } else {
      preview = out.summary ?? out.message ?? out.text ?? out.result ?? "";
    }
  } else if (node.error) {
    preview = node.error;
  }

  return (
    <div className={`wf-node s-${status} cat-${node.spec.category}`}>
      {node.spec.inputs.length > 0 && <Handle type="target" position={Position.Left} id="in" />}
      <div className="wf-head">
        <span className={`wf-badge s-${status}`}>{BADGE[status]}</span>
        <span className="wf-title">{node.spec.display_name}</span>
      </div>
      {preview !== "" && <div className="wf-preview">{String(preview).slice(0, 140)}</div>}
      {node.spec.outputs.length > 0 && <Handle type="source" position={Position.Right} id="out" />}
    </div>
  );
}
