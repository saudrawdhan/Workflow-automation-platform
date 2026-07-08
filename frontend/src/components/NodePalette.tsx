import type { NodeSpec } from "../types";

interface Props {
  specs: NodeSpec[];
  onAdd: (spec: NodeSpec) => void;
}

export default function NodePalette({ specs, onAdd }: Props) {
  return (
    <aside className="palette">
      <h3>Nodes</h3>
      {specs.map((spec) => (
        <button
          key={spec.type}
          className={`pal-item ${spec.category}`}
          onClick={() => onAdd(spec)}
        >
          {spec.display_name}
          <small>{spec.category}</small>
        </button>
      ))}
      {specs.length === 0 && <p className="muted">Start the backend on port 8000.</p>}
    </aside>
  );
}
