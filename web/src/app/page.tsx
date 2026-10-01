import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="mx-auto max-w-5xl px-6 py-24">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium tracking-wide text-neutral-400">
            enterprise_aiops
          </span>
          <nav className="flex gap-4 text-sm text-neutral-400">
            <Link href="/dashboard" className="hover:text-neutral-100">Dashboard</Link>
            <Link href="/events" className="hover:text-neutral-100">Events</Link>
          </nav>
        </div>

        <h1 className="mt-24 text-5xl font-semibold tracking-tight">
          Local operations console
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-neutral-400">
          A live view over the stack running on this machine.
        </p>

        <div className="mt-12 flex gap-4">
          <Button asChild><Link href="/dashboard">Open dashboard</Link></Button>
          <Button variant="outline" asChild><Link href="/events">View events</Link></Button>
        </div>

        <div className="mt-24 grid gap-6 sm:grid-cols-3">
          {[
            { title: "ClickHouse", body: "Event store", href: "/events" },
            { title: "Redis", body: "Cache and queue", href: "/dashboard" },
            { title: "Services", body: "Health and status", href: "/dashboard" },
          ].map((c) => (
            <Link key={c.title} href={c.href}>
              <Card className="border-neutral-800 bg-neutral-900 transition-colors hover:border-neutral-700">
                <CardHeader><CardTitle className="text-base">{c.title}</CardTitle></CardHeader>
                <CardContent className="text-sm text-neutral-400">{c.body}</CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
