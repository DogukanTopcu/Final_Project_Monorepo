"use client";

import { cn } from "@/lib/utils";
import type { ArchitectureMode } from "@/types";

const modes: Array<{ id: ArchitectureMode; title: string; subtitle: string; detail: string }> = [
  {
    id: "monolithic",
    title: "Monolithic",
    subtitle: "One LLM, no orchestration",
    detail: "Baseline ceiling. A single LLM answers every query directly.",
  },
  {
    id: "hybrid",
    title: "Hybrid",
    subtitle: "SLM + LLM cooperation",
    detail: "Routing, multi-agent debate, or speculative drafter+verifier.",
  },
  {
    id: "ensemble",
    title: "Ensemble",
    subtitle: "Multiple SLMs vote",
    detail: "Several small models vote; an LLM may break ties.",
  },
  {
    id: "swarm",
    title: "Swarm",
    subtitle: "Bossless SLM swarm",
    detail: "Bossless SLM swarm variants, with or without a heavy sweeper.",
  },
];

export function ModePicker({
  value,
  onChange,
}: {
  value: ArchitectureMode;
  onChange: (mode: ArchitectureMode) => void;
}) {
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
      {modes.map((mode) => {
        const active = value === mode.id;
        return (
          <button
            key={mode.id}
            type="button"
            onClick={() => onChange(mode.id)}
            className={cn(
              "flex flex-col rounded-lg border p-4 text-left transition",
              active
                ? "border-zinc-900 bg-zinc-900 text-white shadow-sm"
                : "border-zinc-200 bg-white text-zinc-900 hover:border-zinc-400 hover:bg-zinc-50",
            )}
          >
            <div className="text-base font-semibold">{mode.title}</div>
            <div className={cn("text-xs font-medium", active ? "text-zinc-300" : "text-zinc-500")}>
              {mode.subtitle}
            </div>
            <p className={cn("mt-2 text-xs", active ? "text-zinc-300" : "text-zinc-600")}>
              {mode.detail}
            </p>
          </button>
        );
      })}
    </div>
  );
}
