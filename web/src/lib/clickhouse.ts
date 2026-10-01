import { createClient } from "@clickhouse/client";

let client: ReturnType<typeof createClient> | null = null;

export function getCH() {
  if (client) return client;
  client = createClient({
    url: process.env.CLICKHOUSE_URL ?? "http://127.0.0.1:8123",
    username: process.env.CLICKHOUSE_USER ?? "default",
    password: process.env.CLICKHOUSE_PASSWORD ?? "securepassword123",
    database: "default",
  });
  return client;
}
