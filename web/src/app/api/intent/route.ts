import { NextResponse } from "next/server";
import { compile } from "@/lib/dsl/compiler";
import { execute } from "@/lib/dsl/runtime";
import type { Context, Intent } from "@/lib/dsl/types";

export async function POST(req: Request) {
  const body = await req.json();
  const raw: string = body.raw_input ?? "";
  const symbols: string[] = Array.isArray(body.symbols) ? body.symbols : [];

  const intent: Intent = {
    id: `intent-${Date.now()}`,
    raw_input: raw,
    symbols,
  };

  let graph;
  try {
    graph = compile(intent);
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 400 });
  }

  const context: Context = {
    id: "ctx-default",
    entities: [],
    environment: {},
    history: [],
  };

  const executed = await execute(graph, context);

  return NextResponse.json({
    intent,
    graph: executed,
    context,
  });
}
