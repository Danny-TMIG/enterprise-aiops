import type {
  AttributeMap,
  ExecEdge,
  ExecGraph,
  ExecNode,
  Intent,
  Symbol,
} from "./types";
import { SYMBOLS } from "./registry";

function resolveSymbols(ids: string[]): Symbol[] {
  const out: Symbol[] = [];
  for (const id of ids) {
    const s = SYMBOLS[id];
    if (!s) throw new Error(`unknown symbol: ${id}`);
    out.push(s);
  }
  return out;
}

function flattenOperators(symbols: Symbol[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const s of symbols) {
    for (const op of s.expands_to.operators) {
      if (!seen.has(op)) {
        seen.add(op);
        out.push(op);
      }
    }
  }
  return out;
}

function mergeDefaults(symbols: Symbol[]): AttributeMap {
  const out: AttributeMap = {};
  for (const s of symbols) {
    Object.assign(out, s.expands_to.default_params);
  }
  return out;
}

function buildNodes(ops: string[], defaults: AttributeMap): ExecNode[] {
  return ops.map((op) => ({
    id: `${op}-${Math.random().toString(36).slice(2, 8)}`,
    operator: op,
    inputs: { ...defaults },
    outputs: {},
    status: "PENDING" as const,
  }));
}

function autoLink(nodes: ExecNode[]): ExecEdge[] {
  const edges: ExecEdge[] = [];
  for (let i = 0; i < nodes.length - 1; i++) {
    edges.push({ from: nodes[i].id, to: nodes[i + 1].id });
  }
  return edges;
}

export function compile(intent: Intent): ExecGraph {
  const symbols = resolveSymbols(intent.symbols);
  const ops = flattenOperators(symbols);
  const defaults = mergeDefaults(symbols);
  const nodes = buildNodes(ops, defaults);
  const edges = autoLink(nodes);
  return { nodes, edges };
}
