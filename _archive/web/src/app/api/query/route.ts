import { NextResponse } from "next/server";
import { getCH } from "@/lib/clickhouse";

export async function POST(req: Request) {
  const { sql } = await req.json();
  if (typeof sql !== "string" || sql.length > 10_000) {
    return NextResponse.json({ error: "invalid sql" }, { status: 400 });
  }
  // read-only guard
  const forbidden = /\b(insert|update|delete|drop|alter|truncate|create|attach|detach|rename|grant|revoke|kill)\b/i;
  if (forbidden.test(sql)) {
    return NextResponse.json({ error: "read-only queries only" }, { status: 400 });
  }
  try {
    const c = getCH();
    const rs = await c.query({ query: sql, format: "JSONEachRow" });
    const rows = (await rs.json()) as Array<Record<string, unknown>>;
    const columns = rows.length > 0 ? Object.keys(rows[0]) : [];
    return NextResponse.json({ rows, columns });
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 200 });
  }
}
