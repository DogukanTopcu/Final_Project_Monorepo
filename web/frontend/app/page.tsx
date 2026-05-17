"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MetricsChart } from "@/components/MetricsChart";
import { EATSGauge } from "@/components/EATSGauge";
import { useExperiments, useResults } from "@/hooks/useExperiments";
import { formatPercent, formatCost } from "@/lib/utils";

export default function DashboardPage() {
  const { data: experiments } = useExperiments();
  const { data: results } = useResults();

  const totalRuns = experiments?.length ?? 0;
  const completedRuns = experiments?.filter((e) => e.status === "completed") ?? [];
  const avgEats =
    completedRuns.length > 0
      ? completedRuns.reduce((sum, e) => sum + (e.metrics?.eats_score ?? 0), 0) /
        completedRuns.length
      : 0;
  const bestArch = completedRuns.sort(
    (a, b) => (b.metrics?.accuracy ?? 0) - (a.metrics?.accuracy ?? 0),
  )[0];
  const totalCost = completedRuns.reduce(
    (sum, e) => sum + (e.metrics?.total_cost_usd ?? 0),
    0,
  );

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link href="/experiments/new">
          <Button>New Experiment</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Total Runs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{totalRuns}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Avg EATS Score</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{avgEats > 0 ? formatPercent(avgEats) : "—"}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Best Architecture</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold capitalize">
              {bestArch?.architecture.replace("_", " ") ?? "—"}
            </p>
            {bestArch?.metrics?.accuracy != null && (
              <p className="text-sm text-zinc-500">
                {formatPercent(bestArch.metrics.accuracy)} accuracy
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">Total Cost</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{formatCost(totalCost)}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          {results && results.length > 0 ? (
            <MetricsChart results={results} />
          ) : (
            <Card>
              <CardContent className="py-12 text-center text-zinc-500">
                No results yet. Run an experiment to see metrics here.
              </CardContent>
            </Card>
          )}
        </div>
        <div>
          <EATSGauge score={avgEats} label="Average EATS Score" />
        </div>
      </div>
    </div>
  );
}
