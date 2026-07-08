import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
  type Edge,
} from "@xyflow/react";
import { fetchNodeSpecs, runWorkflow } from "./api";
import type { NodeSpec, RunResult, WFNode } from "./types";
import WorkflowNode from "./components/WorkflowNode";
import NodePalette from "./components/NodePalette";
import ConfigPanel from "./components/ConfigPanel";
import RunLog from "./components/RunLog";

let counter = 1;
const nextId = () => `n${counter++}`;

const DEMO_NODES = [
  {
    id: "d1",
    type: "text_input",
    position: { x: 40, y: 160 },
    config: { text: "Delivery was two days late and the box arrived damaged. I would like a refund." },
  },
  { id: "d2", type: "summarize", position: { x: 300, y: 160 }, config: { max_sentences: 2 } },
  {
    id: "d3",
    type: "classify",
    position: { x: 560, y: 160 },
    config: { labels: ["complaint", "request", "praise", "other"] },
  },
  {
    id: "d4",
    type: "message_prep",
    position: { x: 820, y: 160 },
    config: { channel: "email", template: "Subject: {label}\n\n{summary}\n\n— Auto-generated" },
  },
  { id: "d5", type: "output", position: { x: 1080, y: 160 }, config: {} },
];
const DEMO_EDGES: [string, string][] = [
  ["d1", "d2"],
  ["d2", "d3"],
  ["d3", "d4"],
  ["d4", "d5"],
];

export default function App() {
  const [specs, setSpecs] = useState<NodeSpec[]>([]);
  const [nodes, setNodes, onNodesChange] = useNodesState<WFNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [run, setRun] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const rfRef = useRef<any>(null);

  useEffect(() => {
    fetchNodeSpecs()
      .then(setSpecs)
      .catch((e) => setError(e.message));
  }, []);

  const nodeTypes = useMemo(() => ({ workflow: WorkflowNode }), []);

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges],
  );

  const addNode = useCallback(
    (spec: NodeSpec) => {
      const config: Record<string, any> = {};
      Object.entries(spec.params_schema).forEach(([key, schema]: [string, any]) => {
        if ("default" in schema) config[key] = schema.default;
      });
      setNodes((nds) =>
        nds.concat({
          id: nextId(),
          type: "workflow",
          position: { x: 120 + nds.length * 40, y: 80 + nds.length * 30 },
          data: { spec, config, status: "pending", output: null, error: null },
        }),
      );
    },
    [setNodes],
  );

  const loadDemo = useCallback(() => {
    if (specs.length === 0) {
      setError("Start the backend (port 8000), then Load Demo.");
      return;
    }
    const byType = Object.fromEntries(specs.map((s) => [s.type, s]));
    counter = 10;
    setRun(null);
    setError(null);
    setSelectedId(null);
    setNodes(
      DEMO_NODES.map((n) => ({
        id: n.id,
        type: "workflow",
        position: n.position,
        data: { spec: byType[n.type], config: n.config, status: "pending", output: null, error: null },
      })) as WFNode[],
    );
    setEdges(
      DEMO_EDGES.map(([source, target], i) => ({
        id: `de${i}`,
        source,
        target,
        sourceHandle: "out",
        targetHandle: "in",
      })),
    );
    setTimeout(() => rfRef.current?.fitView({ padding: 0.2 }), 60);
  }, [specs, setNodes, setEdges]);

  const clearAll = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setRun(null);
    setError(null);
    setSelectedId(null);
  }, [setNodes, setEdges]);

  const updateConfig = useCallback(
    (id: string, config: Record<string, any>) => {
      setNodes((nds) =>
        nds.map((n) => (n.id === id ? { ...n, data: { ...n.data, config } } : n)),
      );
    },
    [setNodes],
  );

  const toGraph = useCallback(
    () => ({
      id: "current",
      name: "Untitled workflow",
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.data.spec.type,
        position: n.position,
        config: n.data.config,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        source_handle: e.sourceHandle ?? "out",
        target_handle: e.targetHandle ?? "in",
      })),
    }),
    [nodes, edges],
  );

  const onRun = useCallback(async () => {
    setError(null);
    setRunning(true);
    setEdges((eds) => eds.map((e) => ({ ...e, animated: true })));
    try {
      const result = await runWorkflow(toGraph());
      setRun(result);
      const byId = Object.fromEntries(result.node_runs.map((r) => [r.node_id, r]));
      setNodes((nds) =>
        nds.map((n) => {
          const record = byId[n.id];
          return record
            ? { ...n, data: { ...n.data, status: record.status, output: record.output, error: record.error } }
            : n;
        }),
      );
    } catch (e: any) {
      setError(e.message);
    } finally {
      setRunning(false);
      setEdges((eds) => eds.map((e) => ({ ...e, animated: false })));
    }
  }, [toGraph, setNodes, setEdges]);

  const selected = nodes.find((n) => n.id === selectedId) ?? null;

  return (
    <div className="app">
      <header className="toolbar">
        <div className="brand">
          <span className="brand-name">Workflow Automation Platform</span>
          <span className="brand-sub">mini workflow automation</span>
        </div>
        <div className="toolbar-actions">
          <button className="btn ghost" onClick={loadDemo}>
            ✨ Load Demo
          </button>
          <button className="btn ghost" onClick={clearAll} disabled={nodes.length === 0}>
            Clear
          </button>
          <button className="btn run" onClick={onRun} disabled={running || nodes.length === 0}>
            {running ? "Running…" : "▶ Run Workflow"}
          </button>
        </div>
        {error && <span className="err">{error}</span>}
      </header>

      <div className="body">
        <NodePalette specs={specs} onAdd={addNode} />
        <div className="canvas">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={(_, node) => setSelectedId(node.id)}
            onPaneClick={() => setSelectedId(null)}
            onInit={(instance) => { rfRef.current = instance; }}
            fitView
          >
            <Background gap={18} color="#e5e7eb" />
            <Controls />
            <MiniMap pannable zoomable />
          </ReactFlow>
          {nodes.length === 0 && (
            <div className="empty-hint">
              Click <strong>✨ Load Demo</strong> for a ready workflow, or add nodes from the left.
            </div>
          )}
        </div>
        <ConfigPanel node={selected} onChange={updateConfig} />
      </div>

      <RunLog run={run} />
    </div>
  );
}
