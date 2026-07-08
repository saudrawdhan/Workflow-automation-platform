import type { Node } from "@xyflow/react";

export type NodeStatus = "pending" | "running" | "success" | "error" | "skipped";

export interface NodeSpec {
  type: string;
  display_name: string;
  category: string;
  inputs: string[];
  outputs: string[];
  params_schema: Record<string, any>;
}

export interface WFData extends Record<string, unknown> {
  spec: NodeSpec;
  config: Record<string, any>;
  status: NodeStatus;
  output: Record<string, any> | null;
  error: string | null;
}

export type WFNode = Node<WFData, "workflow">;

export interface NodeRunRecord {
  node_id: string;
  type: string;
  status: NodeStatus;
  output: Record<string, any> | null;
  error: string | null;
  ms: number;
  logs: string[];
}

export interface RunResult {
  run_id: string;
  workflow_id: string;
  status: string;
  order: string[];
  node_runs: NodeRunRecord[];
}
