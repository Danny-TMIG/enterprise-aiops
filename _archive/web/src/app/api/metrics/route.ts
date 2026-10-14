import { NextResponse } from "next/server";
import { getCH } from "@/lib/clickhouse";
import { getRedis } from "@/lib/redis";

export async function GET() {
  const out: Record<string, unknown> = {};

  try {
    const c = getCH();
    const rs = await c.query({
      query: `
        SELECT
          count() AS total,
          countIf(timestamp > now() - INTERVAL 1 HOUR) AS last_hour,
          countIf(timestamp > now() - INTERVAL 24 HOUR) AS last_day
        FROM enterprise_aiops.audit_logs
      `,
      format: "JSONEachRow",
    });
    out.clickhouse = (await rs.json())[0];
  } catch (e) {
    out.clickhouse = { error: (e as Error).message };
  }

  try {
    const r = getRedis();
    out.redis = {
      ping: await r.ping(),
      keys: await r.dbsize(),
    };
  } catch (e) {
    out.redis = { error: (e as Error).message };
  }

  return NextResponse.json(out);
}
