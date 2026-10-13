export type SymbolID = string;
export type OperatorID = string;
export type ContextID = string;

export type Vector = number[];
export type Probability = number;
export type Timestamp = number;

export type AttributeMap = Record<string, unknown>;
export type ConstraintMap = Record<string, unknown>;

export interface Expansion {
  operators: OperatorID[];
  constraints: ConstraintMap;
  default_params: AttributeMap;
}

export interface Symbol {
  id: SymbolID;
  embedding?: Vector;
  expands_to: Expansion;
  aliases?: SymbolID[];
  description?: string;
}

export interface Intent {
  id: string;
  raw_input: string;
  symbols: SymbolID[];
  context?: ContextID;
  priority?: number;
}

export interface Operator {
  id: OperatorID;
  description: string;
  input_schema: AttributeMap;
  output_schema: AttributeMap;
  // Every operator is a read/compute/route step. No operator mutates the world.
  kind: "read" | "compute" | "route";
}

export type NodeStatus = "PENDING" | "RUNNING" | "DONE" | "FAILED" | "AWAITING_HUMAN";

export interface ExecNode {
  id: string;
  operator: OperatorID;
  inputs: AttributeMap;
  outputs: AttributeMap;
  status: NodeStatus;
  note?: string;
}

export interface ExecEdge {
  from: string;
  to: string;
  condition?: ConstraintMap;
}

export interface ExecGraph {
  nodes: ExecNode[];
  edges: ExecEdge[];
}

export interface Observation {
  ts: Timestamp;
  features: Vector;
  source: string;
}

export interface Track {
  entity_id: string;
  observations: Observation[];
  continuity_score: Probability;
}

export interface Context {
  id: ContextID;
  entities: string[];
  environment: AttributeMap;
  history: { ts: Timestamp; type: string; payload: AttributeMap }[];
}
