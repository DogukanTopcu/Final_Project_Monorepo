"use client";

import { Slider } from "@/components/ui/slider";
import { Select } from "@/components/ui/select";
import type { ArchitectureParamSpec } from "@/types";

interface ParamControlsProps {
  params: ArchitectureParamSpec[];
  values: Record<string, unknown>;
  onChange: (key: string, value: unknown) => void;
}

export function ParamControls({ params, values, onChange }: ParamControlsProps) {
  if (params.length === 0) {
    return (
      <p className="rounded-md border border-dashed border-zinc-300 p-3 text-xs text-zinc-500">
        No tunable parameters for this architecture.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {params.map((p) => {
        const v = values[p.key] ?? p.default;
        if (p.type === "bool") {
          return (
            <div key={p.key} className="flex items-center gap-2">
              <input
                id={`param-${p.key}`}
                type="checkbox"
                checked={Boolean(v)}
                onChange={(e) => onChange(p.key, e.target.checked)}
                className="h-4 w-4 rounded border-zinc-300"
              />
              <label htmlFor={`param-${p.key}`} className="text-sm text-zinc-700">
                {p.label}
                {p.description ? <span className="text-zinc-500"> — {p.description}</span> : null}
              </label>
            </div>
          );
        }
        if (p.type === "enum") {
          return (
            <Select
              key={p.key}
              label={p.label}
              value={String(v ?? "")}
              onChange={(e) => onChange(p.key, e.target.value)}
            >
              {(p.options ?? []).map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </Select>
          );
        }
        if (p.type === "int" || p.type === "float") {
          const num = Number(v ?? 0);
          const min = p.min ?? 0;
          const max = p.max ?? 1;
          const step = p.type === "int" ? 1 : (max - min) / 100 || 0.01;
          return (
            <div key={p.key} className="space-y-1">
              <Slider
                label={p.label}
                min={min}
                max={max}
                step={step}
                value={num}
                onChange={(e) => {
                  const next = Number(e.target.value);
                  onChange(p.key, p.type === "int" ? Math.trunc(next) : next);
                }}
                displayValue={p.type === "int" ? String(num) : num.toFixed(2)}
              />
              {p.description && <p className="text-[11px] text-zinc-500">{p.description}</p>}
            </div>
          );
        }
        return (
          <div key={p.key} className="space-y-1">
            <label className="text-sm font-medium text-zinc-700">{p.label}</label>
            <input
              type="text"
              value={String(v ?? "")}
              onChange={(e) => onChange(p.key, e.target.value)}
              className="h-10 w-full rounded-md border border-zinc-300 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
            />
            {p.description && <p className="text-[11px] text-zinc-500">{p.description}</p>}
          </div>
        );
      })}
    </div>
  );
}
