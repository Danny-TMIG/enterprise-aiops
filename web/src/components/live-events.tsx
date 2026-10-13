"use client";
import { useEffect, useRef, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Row = {
  timestamp: string;
  event_type: string;
  artifact_id: string;
  details: string;
};

export function LiveEvents() {
  const [rows, setRows] = useState<Row[]>([]);
  const [paused, setPaused] = useState(false);
  const [filter, setFilter] = useState("");
  const [connected, setConnected] = useState(false);
  const pausedRef = useRef(paused);
  pausedRef.current = paused;

  useEffect(() => {
    const es = new EventSource("/api/stream");
    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);
    es.onmessage = (e) => {
      if (pausedRef.current) return;
      const msg = JSON.parse(e.data);
      if (msg.type === "row") {
        setRows((prev) => [msg.row, ...prev].slice(0, 500));
      }
    };
    return () => es.close();
  }, []);

  const filtered = filter
    ? rows.filter(
        (r) =>
          r.event_type?.toLowerCase().includes(filter.toLowerCase()) ||
          r.artifact_id?.toLowerCase().includes(filter.toLowerCase()) ||
          r.details?.toLowerCase().includes(filter.toLowerCase())
      )
    : rows;

  return (
    <div className="mt-8">
      <div className="flex items-center gap-3">
        <Badge variant={connected ? "default" : "destructive"}>
          {connected ? "live" : "disconnected"}
        </Badge>
        <Input
          placeholder="filter…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="max-w-xs"
        />
        <Button
          variant={paused ? "default" : "outline"}
          onClick={() => setPaused((p) => !p)}
        >
          {paused ? "resume" : "pause"}
        </Button>
        <Button variant="outline" onClick={() => setRows([])}>
          clear
        </Button>
        <span className="ml-auto text-sm text-neutral-500">
          {filtered.length} events
        </span>
      </div>

      <div className="mt-4 max-h-[70vh] overflow-auto rounded-lg border border-neutral-800 bg-neutral-950 font-mono text-xs">
        {filtered.map((r, i) => (
          <div
            key={i}
            className="flex gap-3 border-b border-neutral-900 px-3 py-2 hover:bg-neutral-900"
          >
            <span className="w-48 shrink-0 text-neutral-500">
              {String(r.timestamp).slice(0, 23)}
            </span>
            <span className="w-32 shrink-0 text-emerald-400">
              {r.event_type}
            </span>
            <span className="w-40 shrink-0 text-sky-400">{r.artifact_id}</span>
            <span className="text-neutral-300">{r.details}</span>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="px-3 py-6 text-neutral-600">
            waiting for events…
          </div>
        )}
      </div>
    </div>
  );
}
