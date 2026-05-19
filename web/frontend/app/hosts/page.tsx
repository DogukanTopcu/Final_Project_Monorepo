"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useHosts, useModels } from "@/hooks/useExperiments";

export default function HostsPage() {
  const { data, isLoading } = useHosts();
  const { data: models } = useModels();

  const modelsById = new Map(
    [...(models?.slm ?? []), ...(models?.llm ?? [])].map((m) => [m.id, m]),
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Hosts & lock</h1>
        <p className="text-sm text-zinc-600">
          Live status of every physical host serving models. Shared hosts can only run one large
          model at a time — the lock indicator tells you which experiment is currently holding
          the slot.
        </p>
      </div>

      {data?.autoswitch_enabled && (
        <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-800">
          RTX6000 autoswitch is enabled. The backend will run the switch script when an
          experiment needs an alias that is not currently active.
        </div>
      )}

      {isLoading && (
        <p className="text-sm text-zinc-500">Probing hosts…</p>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {data?.hosts.map((host) => {
          const reachableVariant = host.is_reachable
            ? host.active_model_id
              ? "success"
              : "warning"
            : "destructive";
          return (
            <Card key={host.host_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{host.label}</CardTitle>
                  <div className="flex gap-1">
                    {host.shared ? (
                      <Badge variant="warning" className="text-[10px]">
                        shared
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="text-[10px]">
                        dedicated
                      </Badge>
                    )}
                    <Badge variant={reachableVariant} className="text-[10px]">
                      {host.is_reachable ? "reachable" : "unreachable"}
                    </Badge>
                    {host.locked && (
                      <Badge variant="destructive" className="text-[10px]">
                        locked
                      </Badge>
                    )}
                  </div>
                </div>
                {host.base_url && (
                  <p className="text-xs text-zinc-500">{host.base_url}</p>
                )}
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-3 rounded-md border border-zinc-100 bg-zinc-50 p-3 text-xs">
                  <div>
                    <div className="text-zinc-500">Active alias</div>
                    <div className="font-medium text-zinc-900">
                      {host.active_model_id ?? "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-zinc-500">Lock holder</div>
                    <div className="font-medium text-zinc-900">
                      {host.lock_holder ?? "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-zinc-500">Probe latency</div>
                    <div className="font-medium text-zinc-900">
                      {host.last_probe_latency_ms != null
                        ? `${host.last_probe_latency_ms.toFixed(0)} ms`
                        : "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-zinc-500">Served vLLM ids</div>
                    <div className="truncate font-medium text-zinc-900">
                      {host.active_served_ids.length === 0
                        ? "—"
                        : host.active_served_ids[0]}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="mb-1 text-xs font-medium text-zinc-700">
                    Configured aliases
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {host.configured_models.map((mid) => {
                      const model = modelsById.get(mid);
                      const active = mid === host.active_model_id;
                      return (
                        <span
                          key={mid}
                          className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs ${
                            active
                              ? "border-emerald-300 bg-emerald-50 text-emerald-800"
                              : "border-zinc-200 bg-white text-zinc-700"
                          }`}
                        >
                          {mid}
                          {model && !model.configured && (
                            <Badge variant="destructive" className="text-[9px]">
                              env missing
                            </Badge>
                          )}
                        </span>
                      );
                    })}
                  </div>
                </div>

                {host.notes && (
                  <p className="text-xs text-zinc-500">{host.notes}</p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
