"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useModels } from "@/hooks/useExperiments";
import type { ModelInfo } from "@/types";

function ModelRow({ model }: { model: ModelInfo }) {
  return (
    <tr className="border-b border-zinc-100 last:border-0">
      <td className="px-3 py-2">
        <div className="font-medium text-zinc-900">{model.name}</div>
        <div className="text-[11px] text-zinc-500">{model.id}</div>
      </td>
      <td className="px-3 py-2 text-xs text-zinc-600">{model.tier}</td>
      <td className="px-3 py-2 text-xs text-zinc-600">
        {model.host_label ?? "—"}
        {model.shared_host && (
          <Badge variant="warning" className="ml-1 text-[9px]">
            shared
          </Badge>
        )}
      </td>
      <td className="px-3 py-2 text-xs text-zinc-600">{model.runtime_provider}</td>
      <td className="px-3 py-2 text-xs">
        {model.base_url ? (
          <code className="rounded bg-zinc-100 px-1 py-0.5 text-[11px] text-zinc-700">
            {model.base_url}
          </code>
        ) : (
          "—"
        )}
      </td>
      <td className="px-3 py-2 text-xs">
        {model.configured ? (
          model.shared_host && model.is_active_on_host === false ? (
            <Badge variant="warning">configured · idle</Badge>
          ) : (
            <Badge variant="success">ready</Badge>
          )
        ) : (
          <Badge variant="destructive">{model.reason ?? "unavailable"}</Badge>
        )}
      </td>
    </tr>
  );
}

function ModelTable({ title, models }: { title: string; models: ModelInfo[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-200 text-left text-xs uppercase tracking-wider text-zinc-500">
                <th className="px-3 py-2">Model</th>
                <th className="px-3 py-2">Tier</th>
                <th className="px-3 py-2">Host</th>
                <th className="px-3 py-2">Runtime</th>
                <th className="px-3 py-2">Endpoint</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <ModelRow key={m.id} model={m} />
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ModelsPage() {
  const { data, isLoading } = useModels();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Models</h1>
        <p className="text-sm text-zinc-600">
          Every alias the platform knows about, grouped by SLM and LLM tier with host and
          endpoint info. Use this page to validate that an alias is reachable before launching a
          run.
        </p>
      </div>

      {data?.warnings?.length ? (
        <div className="space-y-1">
          {data.warnings.map((w) => (
            <div
              key={w}
              className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800"
            >
              {w}
            </div>
          ))}
        </div>
      ) : null}

      {isLoading ? (
        <p className="text-sm text-zinc-500">Loading models…</p>
      ) : (
        <div className="space-y-6">
          <ModelTable title="SLMs" models={data?.slm ?? []} />
          <ModelTable title="LLMs" models={data?.llm ?? []} />
        </div>
      )}
    </div>
  );
}
