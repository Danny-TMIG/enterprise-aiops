import type { Context, ExecGraph, ExecNode } from "./types";
import { OPERATORS } from "./registry";

// Every operator here is read / compute / route. None mutates an external system.
async function runOperator(op: string, inputs: Record<string, unknown>): Promise<Record<string, unknown>> {
  switch (op) {
    case "fetch_posts":
      // Wire this to your ClickHouse table.
      return { posts: [], note: "wire fetch_posts to your data source" };

    case "embed_text":
      // Wire this to your embedding provider.
      return { vectors: [], note: "wire embed_text to your embedding provider" };

    case "cluster_embeddings":
      return { clusters: [], note: "wire cluster_embeddings to a clustering backend" };

    case "score_coordination":
      return { scores: {}, note: "wire score_coordination to your detector" };

    case "score_similarity":
      return { matrix: [], note: "wire score_similarity to your similarity backend" };

    case "summarize":
      return { summary: "", note: "wire summarize to your summarizer" };

    case "route_to_analyst":
      return { ticket_id: `REV-${Date.now()}`, note: "queued for human review" };

    case "flag_for_review":
      return { flagged: true, note: "queued for human review; no automated action" };

    case "notify_platform":
      // Deliberately a no-op that requires a downstream human approval step.
      return { sent: false, requires_approval: true };

    default:
      throw new Error(`unknown operator: ${op}`);
  }
}

export async function execute(graph: ExecGraph, context: Context): Promise<ExecGraph> {
  const out: ExecGraph = JSON.parse(JSON.stringify(graph));

  for (const node of out.nodes) {
    // Route-class operators always pause for a human.
    const op = OPERATORS[node.operator];
    if (op?.kind === "route" && node.operator === "notify_platform") {
      node.status = "AWAITING_HUMAN";
      node.note = "human approval required before any external notification";
      continue;
    }

    node.status = "RUNNING";
    try {
      const result = await runOperator(node.operator, node.inputs);
      node.outputs = result as Record<string, unknown>;
      node.status = op?.kind === "route" ? "AWAITING_HUMAN" : "DONE";
      if (op?.kind === "route") {
        node.note = "queued for human review";
      }
      context.history.push({
        ts: Date.now(),
        type: "operator_complete",
        payload: { operator: node.operator, id: node.id },
      });
    } catch (e) {
      node.status = "FAILED";
      node.note = (e as Error).message;
    }
  }

  return out;
}

export function updateObservation(
  track: { observations: { ts: number; features: number[]; source: string }[]; continuity_score: number },
  obs: { ts: number; features: number[]; source: string }
) {
  track.observations.push(obs);
  track.continuity_score = estimateContinuity(track.observations);
}

function estimateContinuity(obs: { ts: number; features: number[] }[]): number {
  if (obs.length < 2) return 0;
  const a = obs[obs.length - 2].features;
  const b = obs[obs.length - 1].features;
  const dot = a.reduce((s, x, i) => s + x * (b[i] ?? 0), 0);
  const na = Math.sqrt(a.reduce((s, x) => s + x * x, 0));
  const nb = Math.sqrt(b.reduce((s, x) => s + x * x, 0));
  return na && nb ? Math.max(0, Math.min(1, dot / (na * nb))) : 0;
}
