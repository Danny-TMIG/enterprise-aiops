"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Item = { label: string; href?: string; run?: () => void };

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const router = useRouter();

  const items: Item[] = [
    { label: "Home", href: "/" },
    { label: "Dashboard", href: "/dashboard" },
    { label: "Events", href: "/events" },
    { label: "Query", href: "/query" },
    { label: "Reload page", run: () => location.reload() },
  ];

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  if (!open) return null;

  const filtered = items.filter((i) =>
    i.label.toLowerCase().includes(q.toLowerCase())
  );

  const exec = (i: Item) => {
    setOpen(false);
    setQ("");
    if (i.href) router.push(i.href);
    if (i.run) i.run();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 p-24"
      onClick={() => setOpen(false)}
    >
      <div
        className="w-full max-w-lg rounded-lg border border-neutral-800 bg-neutral-900 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          autoFocus
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Type a command…"
          className="w-full border-b border-neutral-800 bg-transparent px-4 py-3 text-sm outline-none"
        />
        <ul className="max-h-80 overflow-auto py-2">
          {filtered.map((i) => (
            <li
              key={i.label}
              onClick={() => exec(i)}
              className="cursor-pointer px-4 py-2 text-sm hover:bg-neutral-800"
            >
              {i.label}
            </li>
          ))}
          {filtered.length === 0 && (
            <li className="px-4 py-2 text-sm text-neutral-500">no matches</li>
          )}
        </ul>
      </div>
    </div>
  );
}
