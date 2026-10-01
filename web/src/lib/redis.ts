import Redis from "ioredis";

let client: Redis | null = null;

export function getRedis() {
  if (client) return client;
  client = new Redis(process.env.REDIS_URL ?? "redis://127.0.0.1:6379", {
    lazyConnect: false,
    maxRetriesPerRequest: 1,
  });
  return client;
}
