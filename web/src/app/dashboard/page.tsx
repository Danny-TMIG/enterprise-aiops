"use client";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type Metrics = {
  clickhouse?: { total?: number; last_hour?: number; last_day?: number; error?: string };
  redis?: { ping?: string; keys?: number; error?: string };
};

function useMetrics() {
  const [data, setData] = useState<Metrics | null>(null);
  useEffect(() => {
    const tick = () =>
      fetch("/api/metrics").then((r) => r.json()).then(setData).catch(() => {});
    tick();
    const id = setInterval(tick, 5000);
    return () => clearInterval(id);
  }, []);
  return data;
}

function Metric({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <Card className="border-neutral-800 bg-neutral-900">
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-sm font-normal text-neutral-400">{label}</CardTitle>
        {sub && <Badge variant="outline">{sub}</Badge>}
      </CardHeader>
      <CardContent className="text-3xl font-semibold">{value}</CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const m = useMetrics();
  const ch = m?.clickhouse;
  const rd = m?.redis;

  return (
    <main className="min-h-screen bg-neutral-950 p-12 text-neutral-100">
      <h1 className="text-3xl font-semibold">Dashboard</h1>
      <p className="mt-2 text-neutral-400">Live metrics, refreshed every 5s.</p>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Metric
          label="Events (total)"
          value={ch?.error ? "—" : String(ch?.total ?? "…")}
          sub={ch?.error ? "down" : undefined}
        />
        <Metric
          label="Events (1h)"
          value={ch?.error ? "—" : String(ch?.last_hour ?? "…")}
        />
        <Metric
          label="Events (24h)"
          value={ch?.error ? "—" : String(ch?.last_day ?? "…")}
        />
        <Metric
          label="Redis keys"
          value={rd?.error ? "—" : String(rd?.keys ?? "…")}
          sub={rd?.ping ?? undefined}
        />
      </div>

      {ch?.error && (
        <pre className="mt-8 rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          ClickHouse: {ch.error}
        </pre>
      )}
      {rd?.error && (
        <pre className="mt-2 rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          Redis: {rd.error}
        </pre>
      )}
    </main>
  );
}
