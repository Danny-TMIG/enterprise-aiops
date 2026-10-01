import { LiveEvents } from "@/components/live-events";

export default function Events() {
  return (
    <main className="min-h-screen bg-neutral-950 p-12 text-neutral-100">
      <h1 className="text-3xl font-semibold">Events</h1>
      <p className="mt-2 text-neutral-400">Live stream from ClickHouse.</p>
      <LiveEvents />
    </main>
  );
}
