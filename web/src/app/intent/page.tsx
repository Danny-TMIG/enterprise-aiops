"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

type Node = {
  id: string;
  operator: string;
  status: string;
  note?: string;
  outputs: Record<string, unknown>;
};

export default function IntentPage() {
  const [raw, setRaw] = useState("find coordinated amplification of this narrative");
  const [symbols, setSymbols] = useState("amplification, coordination");
  const [graph, setGraph] = useState<{ nodes: Node[] } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true);
    setError(null);
    setGraph(null);
    try {
      const r = await fetch("/api/intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_input: raw,
          symbols: symbols.split(",").map((s) => s.trim()).filter(Boolean),
        }),
      });
      const j = await r.json();
      if (j.error) setError(j.error);
      else setGraph(j.graph);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen bg-neutral-950 p-12 text-neutral-100">
      <h1 className="text-3xl font-semibold">Intent → Graph</h1>
      <p className="mt-2 text-neutral-400">
        Digital-target DSL. All operators are read, compute, or route-to-human. No operator acts on the world.
      </p>

      <div className="mt-8 space-y-3 max-w-2xl">
        <Input value={raw} onChange={(e) => setRaw(e.target.value)} placeholder="raw input" />
        <Input value={symbols} onChange={(e) => setSymbols(e.target.value)} placeholder="symbols, comma separated" />
        <div className="text-xs text-neutral-500">
          available symbols: narrative, coordination, amplification, review, indicator
        </div>
        <Button onClick={run} disabled={busy}>{busy ? "compiling…" : "compile and run"}</Button>
      </div>

      {error && (
        <pre className="mt-6 max-w-2xl rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </pre>
      )}

      {graph && (
        <div className="mt-8 space-y-3">
          {graph.nodes.map((n) => (
            <div key={n.id} className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm text-sky-400">{n.operator}</span>
                <Badge
                  variant={
                    n.status === "DONE" ? "default" :
                    n.status === "AWAITING_HUMAN" ? "outline" :
                    n.status === "FAILED" ? "destructive" : "secondary"
                  }
                >
                  {n.status}
                </Badge>
              </div>
              {n.note && <div className="mt-2 text-xs text-neutral-500">{n.note}</div>}
              <pre className="mt-2 text-xs text-neutral-400 overflow-auto">
                {JSON.stringify(n.outputs, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
