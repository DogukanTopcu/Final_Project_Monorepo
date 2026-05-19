"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navGroups: Array<{
  title: string;
  items: Array<{ href: string; label: string; matchPrefix?: string }>;
}> = [
  {
    title: "Operate",
    items: [
      { href: "/", label: "Dashboard" },
      { href: "/playground", label: "Playground" },
      { href: "/hosts", label: "Hosts & Lock" },
      { href: "/models", label: "Models" },
    ],
  },
  {
    title: "Experiments",
    items: [
      { href: "/experiments/new", label: "Launch experiment" },
      {
        href: "/experiments",
        label: "All experiments",
        matchPrefix: "/experiments",
      },
    ],
  },
  {
    title: "Results & Analysis",
    items: [
      { href: "/results", label: "Results" },
      { href: "/analysis", label: "Analysis" },
    ],
  },
  {
    title: "Infra",
    items: [{ href: "/infrastructure", label: "EC2 & costs" }],
  },
];

export function SideNav() {
  const pathname = usePathname();

  function isActive(href: string, matchPrefix?: string) {
    if (matchPrefix) {
      return pathname === href || pathname.startsWith(`${matchPrefix}/`);
    }
    return pathname === href;
  }

  return (
    <aside className="flex w-60 flex-col border-r border-zinc-200 bg-white px-4 py-6">
      <div className="mb-6">
        <h1 className="text-base font-bold text-zinc-900">Thesis Platform</h1>
        <p className="text-xs text-zinc-500">SLM / LLM experiment runner</p>
      </div>
      <nav className="flex-1 space-y-5 overflow-y-auto">
        {navGroups.map((group) => (
          <div key={group.title}>
            <div className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
              {group.title}
            </div>
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "block rounded-md px-3 py-1.5 text-sm font-medium transition",
                    isActive(item.href, item.matchPrefix)
                      ? "bg-zinc-900 text-white"
                      : "text-zinc-700 hover:bg-zinc-100 hover:text-zinc-900",
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </nav>
      <div className="mt-6 border-t border-zinc-100 pt-3 text-[11px] text-zinc-500">
        Backend: {process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"}
      </div>
    </aside>
  );
}
