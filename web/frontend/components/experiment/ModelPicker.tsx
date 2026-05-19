"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { ModelInfo } from "@/types";

interface ModelPickerProps {
  label: string;
  description?: string;
  models: ModelInfo[];
  value: string;
  onChange: (modelId: string) => void;
  emptyMessage?: string;
}

export function ModelPicker({
  label,
  description,
  models,
  value,
  onChange,
  emptyMessage = "No models available",
}: ModelPickerProps) {
  // Group by host so the shared-host alias clusters are visible.
  const byHost = new Map<string, ModelInfo[]>();
  for (const model of models) {
    const key = model.host_label ?? model.host_id ?? "Other";
    if (!byHost.has(key)) byHost.set(key, []);
    byHost.get(key)!.push(model);
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-zinc-900">{label}</div>
          {description && <div className="text-xs text-zinc-500">{description}</div>}
        </div>
        {value && (
          <span className="text-xs text-zinc-500">{value}</span>
        )}
      </div>
      {models.length === 0 ? (
        <div className="rounded-md border border-dashed border-zinc-300 p-3 text-xs text-zinc-500">
          {emptyMessage}
        </div>
      ) : (
        <div className="space-y-3">
          {Array.from(byHost.entries()).map(([hostLabel, hostModels]) => (
            <div key={hostLabel}>
              <div className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
                {hostLabel}
              </div>
              <div className="grid grid-cols-1 gap-1.5">
                {hostModels.map((model) => {
                  const active = model.id === value;
                  const disabled = !model.configured;
                  const inactive = model.shared_host && model.is_active_on_host === false;
                  return (
                    <button
                      key={model.id}
                      type="button"
                      disabled={disabled}
                      onClick={() => onChange(model.id)}
                      className={cn(
                        "flex w-full items-center justify-between rounded-md border px-3 py-2 text-left text-sm transition",
                        active
                          ? "border-zinc-900 bg-zinc-900 text-white"
                          : disabled
                            ? "cursor-not-allowed border-zinc-200 bg-zinc-50 text-zinc-400"
                            : "border-zinc-200 bg-white text-zinc-900 hover:border-zinc-400 hover:bg-zinc-50",
                      )}
                    >
                      <div className="flex flex-col">
                        <span className="font-medium">{model.name}</span>
                        <span className={cn("text-[11px]", active ? "text-zinc-300" : "text-zinc-500")}>
                          {model.id} · {model.tier}
                        </span>
                      </div>
                      <div className="flex shrink-0 items-center gap-1">
                        {disabled && (
                          <Badge variant="destructive" className="text-[10px]">
                            unavailable
                          </Badge>
                        )}
                        {!disabled && inactive && (
                          <Badge variant="warning" className="text-[10px]">
                            needs switch
                          </Badge>
                        )}
                        {!disabled && model.is_active_on_host && (
                          <Badge variant="success" className="text-[10px]">
                            active
                          </Badge>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
