import { NextResponse } from "next/server";
import { getCH } from "@/lib/clickhouse";

export async function GET() {
  try {
    const c = getCH();
    await c.command({ query: "CREATE DATABASE IF NOT EXISTS enterprise_aiops" });
    await c.command({
      query: `
        CREATE TABLE IF NOT EXISTS enterprise_aiops.audit_logs (
          timestamp DateTime64(3, 'UTC'),
          event_type LowCardinality(String),
          artifact_id String,
          details String
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, event_type)
      `,
    });
    const rs = await c.query({
      query:
        "SELECT timestamp, event_type, artifact_id, details FROM enterprise_aiops.audit_logs ORDER BY timestamp DESC LIMIT 50",
      format: "JSONEachRow",
    });
    const rows = await rs.json();
    return NextResponse.json({ rows });
  } catch (e) {
    return NextResponse.json({ rows: [], error: (e as Error).message }, { status: 200 });
  }
}
