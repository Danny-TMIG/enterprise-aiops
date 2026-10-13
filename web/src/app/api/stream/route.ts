import { getCH } from "@/lib/clickhouse";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  const encoder = new TextEncoder();
  let lastTs = new Date(Date.now() - 60_000).toISOString().replace("T", " ").slice(0, 23);

  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: unknown) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
      };

      send({ type: "ready" });

      const tick = async () => {
        try {
          const c = getCH();
          const rs = await c.query({
            query: `
              SELECT timestamp, event_type, artifact_id, details
              FROM enterprise_aiops.audit_logs
              WHERE timestamp > {last:DateTime64(3)}
              ORDER BY timestamp ASC
              LIMIT 100
            `,
            query_params: { last: lastTs },
            format: "JSONEachRow",
          });
          const rows = (await rs.json()) as Array<Record<string, unknown>>;
          for (const r of rows) {
            send({ type: "row", row: r });
            lastTs = String(r.timestamp);
          }
        } catch (e) {
          send({ type: "error", message: (e as Error).message });
        }
      };

      const interval = setInterval(tick, 2000);
      tick();

      // @ts-expect-error controller is closed by abort
      controller._cleanup = () => clearInterval(interval);
    },
    cancel() {
      // handled by interval clear in the closure
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
