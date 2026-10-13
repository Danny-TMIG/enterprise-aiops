import type { Operator, Symbol } from "./types";

// Operator registry. Read-only / compute / route only.
export const OPERATORS: Record<string, Operator> = {
  fetch_posts: {
    id: "fetch_posts",
    description: "Read posts matching a query from a data source.",
    kind: "read",
    input_schema: { query: "string", limit: "int" },
    output_schema: { posts: "Post[]" },
  },
  embed_text: {
    id: "embed_text",
    description: "Compute embeddings for a list of texts.",
    kind: "compute",
    input_schema: { texts: "string[]" },
    output_schema: { vectors: "Vector[]" },
  },
  cluster_embeddings: {
    id: "cluster_embeddings",
    description: "Cluster vectors and return cluster assignments.",
    kind: "compute",
    input_schema: { vectors: "Vector[]", k: "int" },
    output_schema: { clusters: "int[]" },
  },
  score_coordination: {
    id: "score_coordination",
    description: "Score how coordinated a set of accounts is, based on timing and overlap.",
    kind: "compute",
    input_schema: { accounts: "string[]" },
    output_schema: { scores: "map<string, float>" },
  },
  score_similarity: {
    id: "score_similarity",
    description: "Score pairwise semantic similarity within a cluster.",
    kind: "compute",
    input_schema: { vectors: "Vector[]" },
    output_schema: { matrix: "float[][]" },
  },
  summarize: {
    id: "summarize",
    description: "Summarize a set of posts into a short narrative.",
    kind: "compute",
    input_schema: { posts: "Post[]" },
    output_schema: { summary: "string" },
  },
  route_to_analyst: {
    id: "route_to_analyst",
    description: "Create a review item in the analyst queue. Never acts on the target.",
    kind: "route",
    input_schema: { subject: "string", evidence: "AttributeMap" },
    output_schema: { ticket_id: "string" },
  },
  flag_for_review: {
    id: "flag_for_review",
    description: "Flag content for human review. No automated enforcement.",
    kind: "route",
    input_schema: { content_id: "string", reason: "string" },
    output_schema: { flagged: "bool" },
  },
  notify_platform: {
    id: "notify_platform",
    description: "Emit an indicator to a partner platform. Requires operator approval downstream.",
    kind: "route",
    input_schema: { indicator: "AttributeMap" },
    output_schema: { sent: "bool", requires_approval: "true" },
  },
};

// Symbol table. Names are neutral; expansions are detection steps.
export const SYMBOLS: Record<string, Symbol> = {
  narrative: {
    id: "narrative",
    description: "A recurring story or framing across accounts.",
    expands_to: {
      operators: ["fetch_posts", "embed_text", "cluster_embeddings", "summarize"],
      constraints: { limit: 500 },
      default_params: { k: 8 },
    },
  },
  coordination: {
    id: "coordination",
    description: "Accounts acting together in a way that suggests a shared operator.",
    expands_to: {
      operators: ["fetch_posts", "score_coordination", "route_to_analyst"],
      constraints: {},
      default_params: {},
    },
  },
  amplification: {
    id: "amplification",
    description: "A cluster of accounts boosting the same content in a short window.",
    expands_to: {
      operators: ["fetch_posts", "score_coordination", "score_similarity", "flag_for_review"],
      constraints: {},
      default_params: {},
    },
  },
  review: {
    id: "review",
    description: "Send something to the human analyst queue.",
    expands_to: {
      operators: ["route_to_analyst"],
      constraints: {},
      default_params: {},
    },
  },
  indicator: {
    id: "indicator",
    description: "A non-personal signal that can be shared with partner platforms.",
    expands_to: {
      operators: ["notify_platform"],
      constraints: {},
      default_params: {},
    },
  },
};

// Aliases. Kept minimal on purpose.
SYMBOLS["campaign"] = { ...SYMBOLS["narrative"], aliases: ["narrative"] };
SYMBOLS["botnet"] = { ...SYMBOLS["coordination"], aliases: ["coordination"] };
