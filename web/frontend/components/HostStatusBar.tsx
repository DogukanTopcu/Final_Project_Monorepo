"use client";

import Link from "next/link";
import { useHosts } from "@/hooks/useExperiments";
import { Badge } from "@/components/ui/badge";

export function HostStatusBar() {
  const { data } = useHosts();
  const sharedHosts = (data?.hosts ?? []).filter((h) => h.shared);

  if (!sharedHosts.length) {
    return (
      <div className="border-b border-zinc-200 bg-white px-6 py-2 text-xs text-zinc-500">
        Loading host status…
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 border-b border-zinc-200 bg-white px-6 py-2 text-xs">
      <span className="font-medium text-zinc-600">Shared hosts</span>
      <div className="flex flex-wrap items-center gap-2">
        {sharedHosts.map((host) => {
          const active = host.active_model_id;
          const locked = host.locked;
          return (
            <Link
              key={host.host_id}
              href="/hosts"
              className="inline-flex items-center gap-1 rounded-full border border-zinc-200 px-2.5 py-0.5 hover:border-zinc-400 hover:bg-zinc-50"
            >
              <span
                className={`inline-block h-2 w-2 rounded-full ${
                  host.is_reachable
                    ? active
                      ? "bg-emerald-500"
                      : "bg-amber-500"
                    : "bg-zinc-300"
                }`}
                aria-hidden
              />
              <span className="font-medium text-zinc-700">{host.label}</span>
              <span className="text-zinc-500">
                {active ?? (host.is_reachable ? "no alias matched" : "unreachable")}
              </span>
              {locked && (
                <Badge variant="warning" className="ml-1 text-[10px]">
                  locked: {host.lock_holder}
                </Badge>
              )}
            </Link>
          );
        })}
      </div>
      {data?.autoswitch_enabled && (
        <Badge variant="success" className="text-[10px]">
          autoswitch on
        </Badge>
      )}
    </div>
  );
}
