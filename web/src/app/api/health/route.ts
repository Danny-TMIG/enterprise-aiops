import { NextResponse } from "next/server";
import { getCH } from "@/lib/clickhouse";
import { getRedis } from "@/lib/redis";

export async function GET() {
  const out: Record<string, unknown> = { redis: null, clickhouse: null };

  try {
    const r = await getRedis().ping();
    out.redis = r;
  } catch (e) {
    out.redis = `error: ${(e as Error).message}`;
  }

  try {
    const c = getCH();
    out.clickhouse = await c.command({ query: "SELECT 1" });
  } catch (e) {
    out.clickhouse = `error: ${(e as Error).message}`;
  }

  return NextResponse.json(out);
}
