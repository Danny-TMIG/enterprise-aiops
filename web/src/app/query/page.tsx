"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function Query() {
  const [sql, setSql] = useState("SELECT * FROM enterprise_aiops.audit_logs ORDER BY timestamp DESC LIMIT 100");
  const [rows, setRows] = useState<Array<Record<string, unknown>>>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true);
    setError(null);
    const t0 = performance.now();
    try {
      const r = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sql }),
      });
      const j = await r.json();
      setElapsed(performance.now() - t0);
      if (j.error) {
        setError(j.error);
        setRows([]);
        setColumns([]);
      } else {
        setRows(j.rows ?? []);
        setColumns(j.columns ?? []);
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen bg-neutral-950 p-12 text-neutral-100">
      <h1 className="text-3xl font-semibold">Query</h1>
      <p className="mt-2 text-neutral-400">Read-only SQL against ClickHouse.</p>

      <textarea
        value={sql}
        onChange={(e) => setSql(e.target.value)}
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === "Enter") run();
        }}
        className="mt-6 h-32 w-full rounded-lg border border-neutral-800 bg-neutral-900 p-3 font-mono text-sm"
      />

      <div className="mt-3 flex items-center gap-3">
        <Button onClick={run} disabled={busy}>
          {busy ? "running…" : "run  ⌘↵"}
        </Button>
        {elapsed !== null && (
          <span className="text-sm text-neutral-500">{elapsed.toFixed(0)} ms</span>
        )}
        <span className="text-sm text-neutral-500">{rows.length} rows</span>
      </div>

      {error && (
        <pre className="mt-6 rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </pre>
      )}

      {columns.length > 0 && (
        <div className="mt-6 max-h-[60vh] overflow-auto rounded-lg border border-neutral-800">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-neutral-900">
              <tr>
                {columns.map((c) => (
                  <th key={c} className="border-b border-neutral-800 px-3 py-2 text-left font-mono text-xs text-neutral-400">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="hover:bg-neutral-900">
                  {columns.map((c) => (
                    <td key={c} className="border-b border-neutral-900 px-3 py-1 font-mono text-xs">
                      {String(r[c] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
