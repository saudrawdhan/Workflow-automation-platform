import type { WFNode } from "../types";

interface Props {
  node: WFNode | null;
  onChange: (id: string, config: Record<string, any>) => void;
}

export default function ConfigPanel({ node, onChange }: Props) {
  if (!node) {
    return (
      <aside className="config">
        <p className="muted">Select a node to edit it.</p>
      </aside>
    );
  }

  const { spec, config, error } = node.data;
  const set = (key: string, value: any) => onChange(node.id, { ...config, [key]: value });

  return (
    <aside className="config">
      <h3>{spec.display_name}</h3>
      {Object.entries(spec.params_schema).map(([key, schema]: [string, any]) => (
        <label key={key} className="field">
          <span>{key}</span>
          {schema.widget === "textarea" ? (
            <textarea
              rows={4}
              value={config[key] ?? ""}
              onChange={(e) => set(key, e.target.value)}
            />
          ) : schema.type === "enum" ? (
            <select value={config[key] ?? schema.default} onChange={(e) => set(key, e.target.value)}>
              {schema.options.map((option: string) => (
                <option key={option}>{option}</option>
              ))}
            </select>
          ) : String(schema.type).startsWith("list") ? (
            <input
              value={(config[key] ?? []).join(", ")}
              onChange={(e) =>
                set(
                  key,
                  e.target.value
                    .split(",")
                    .map((v) => v.trim())
                    .filter(Boolean),
                )
              }
            />
          ) : schema.type === "integer" ? (
            <input
              type="number"
              value={config[key] ?? schema.default ?? 0}
              onChange={(e) => set(key, Number(e.target.value))}
            />
          ) : (
            <input value={config[key] ?? ""} onChange={(e) => set(key, e.target.value)} />
          )}
        </label>
      ))}
      {error && <p className="err">{error}</p>}
    </aside>
  );
}
