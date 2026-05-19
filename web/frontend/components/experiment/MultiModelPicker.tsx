"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { ModelInfo } from "@/types";

interface MultiModelPickerProps {
  label: string;
  description?: string;
  models: ModelInfo[];
  value: string[];
  onChange: (modelIds: string[]) => void;
  min?: number;
  max?: number;
}

export function MultiModelPicker({
  label,
  description,
  models,
  value,
  onChange,
  min = 1,
  max = 8,
}: MultiModelPickerProps) {
  const toggle = (id: string) => {
    if (value.includes(id)) {
      // allow drop unless it would go below `min` and we still have other choices
      onChange(value.filter((m) => m !== id));
    } else if (value.length < max) {
      onChange([...value, id]);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-zinc-900">{label}</div>
          {description && <div className="text-xs text-zinc-500">{description}</div>}
        </div>
        <span className="text-xs text-zinc-500">
          {value.length} selected (min {min}, max {max})
        </span>
      </div>
      {models.length === 0 ? (
        <div className="rounded-md border border-dashed border-zinc-300 p-3 text-xs text-zinc-500">
          No SLMs available.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-1.5 md:grid-cols-2">
          {models.map((model) => {
            const selected = value.includes(model.id);
            const disabled = !model.configured;
            const order = value.indexOf(model.id);
            return (
              <button
                key={model.id}
                type="button"
                disabled={disabled}
                onClick={() => toggle(model.id)}
                className={cn(
                  "flex items-center justify-between rounded-md border px-3 py-2 text-left text-sm transition",
                  selected
                    ? "border-zinc-900 bg-zinc-900 text-white"
                    : disabled
                      ? "cursor-not-allowed border-zinc-200 bg-zinc-50 text-zinc-400"
                      : "border-zinc-200 bg-white text-zinc-900 hover:border-zinc-400 hover:bg-zinc-50",
                )}
              >
                <div className="flex flex-col">
                  <span className="font-medium">{model.name}</span>
                  <span className={cn("text-[11px]", selected ? "text-zinc-300" : "text-zinc-500")}>
                    {model.id} · {model.host_label ?? model.tier}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  {disabled && (
                    <Badge variant="destructive" className="text-[10px]">
                      unavailable
                    </Badge>
                  )}
                  {selected && (
                    <Badge variant="secondary" className="text-[10px]">
                      #{order + 1}
                    </Badge>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
