"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricsChart } from "@/components/MetricsChart";
import { EATSGauge } from "@/components/EATSGauge";
import { useExperiments, useHosts, useResults } from "@/hooks/useExperiments";
import { formatCost, formatDecimal, formatDurationMs, formatPercent } from "@/lib/utils";

export default function DashboardPage() {
  const { data: experiments } = useExperiments();
  const { data: results } = useResults();
  const { data: hosts } = useHosts();

  const totalRuns = experiments?.length ?? 0;
  const completedRuns = experiments?.filter((e) => e.status === "completed") ?? [];
  const runningRuns = experiments?.filter((e) => e.status === "running") ?? [];
  const avgEats =
    completedRuns.length > 0
      ? completedRuns.reduce((sum, e) => sum + (e.metrics?.eats_score ?? 0), 0) /
        completedRuns.length
      : 0;
  const bestArch = [...completedRuns].sort(
    (a, b) => (b.metrics?.accuracy ?? 0) - (a.metrics?.accuracy ?? 0),
  )[0];
  const totalCost = completedRuns.reduce(
    (sum, e) => sum + (e.metrics?.total_cost_usd ?? 0),
    0,
  );
  const recent = (experiments ?? []).slice(0, 5);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-sm text-zinc-600">
            Status of the experiment platform, hosts and recent runs.
          </p>
        </div>
        <Link href="/experiments/new">
          <Button>New experiment</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Total runs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{totalRuns}</p>
            <p className="text-xs text-zinc-500">
              {runningRuns.length} running · {completedRuns.length} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Average EATS</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{avgEats > 0 ? formatDecimal(avgEats, 2) : "—"}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Best architecture</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold capitalize">
              {bestArch?.architecture.replace(/_/g, " ") ?? "—"}
            </p>
            {bestArch?.metrics?.accuracy != null && (
              <p className="text-xs text-zinc-500">
                {formatPercent(bestArch.metrics.accuracy)} accuracy
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Total cost</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{formatCost(totalCost)}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          {results && results.length > 0 ? (
            <MetricsChart results={results} />
          ) : (
            <Card>
              <CardContent className="py-12 text-center text-zinc-500">
                No results yet. Run an experiment to see metrics here.
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Recent experiments</CardTitle>
            </CardHeader>
            <CardContent>
              {recent.length === 0 ? (
                <p className="text-sm text-zinc-500">No experiments yet.</p>
              ) : (
                <ul className="divide-y divide-zinc-100 text-sm">
                  {recent.map((exp) => (
                    <li key={exp.experiment_id} className="flex items-center justify-between py-2">
                      <Link
                        href={`/experiments/${exp.experiment_id}`}
                        className="flex flex-1 items-center gap-2"
                      >
                        <span className="font-mono text-xs text-zinc-500">
                          {exp.experiment_id}
                        </span>
                        <Badge variant="outline" className="text-[10px]">
                          {exp.architecture}
                        </Badge>
                        <span className="text-xs text-zinc-500">{exp.benchmark}</span>
                      </Link>
                      <div className="flex items-center gap-2 text-xs text-zinc-500">
                        <Badge
                          variant={
                            exp.status === "completed"
                              ? "success"
                              : exp.status === "running"
                                ? "warning"
                                : exp.status === "failed"
                                  ? "destructive"
                                  : "secondary"
                          }
                        >
                          {exp.status}
                        </Badge>
                        {exp.metrics?.accuracy != null && (
                          <span>{formatPercent(exp.metrics.accuracy)}</span>
                        )}
                        {exp.metrics?.avg_latency_ms != null && (
                          <span>{formatDurationMs(exp.metrics.avg_latency_ms)}</span>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
        <div className="space-y-4">
          <EATSGauge score={avgEats} label="Average EATS score" />

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Shared host status</CardTitle>
            </CardHeader>
            <CardContent>
              {hosts?.hosts.filter((h) => h.shared).length ? (
                <ul className="space-y-2 text-sm">
                  {hosts.hosts
                    .filter((h) => h.shared)
                    .map((h) => (
                      <li key={h.host_id} className="rounded-md border border-zinc-200 p-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-medium text-zinc-900">{h.label}</span>
                          <Badge variant={h.is_reachable ? "success" : "destructive"}>
                            {h.is_reachable ? "online" : "offline"}
                          </Badge>
                        </div>
                        <div className="mt-1 text-xs text-zinc-600">
                          Active: {h.active_model_id ?? "—"}
                          {h.locked && (
                            <span className="ml-2 text-amber-700">
                              locked · {h.lock_holder ?? "?"}
                            </span>
                          )}
                        </div>
                      </li>
                    ))}
                </ul>
              ) : (
                <p className="text-xs text-zinc-500">No shared hosts configured.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
