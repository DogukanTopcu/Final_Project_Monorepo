"use client";

import { use } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LiveProgress } from "@/components/LiveProgress";
import { EATSGauge } from "@/components/EATSGauge";
import { useExperiment } from "@/hooks/useExperiments";
import { formatDate, formatPercent, formatCost } from "@/lib/utils";

export default function ExperimentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: experiment, isLoading } = useExperiment(id);

  if (isLoading) {
    return <p className="text-zinc-500">Loading experiment...</p>;
  }

  if (!experiment) {
    return <p className="text-red-600">Experiment not found.</p>;
  }

  const isActive = experiment.status === "running" || experiment.status === "queued";

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/experiments" className="text-zinc-500 hover:text-zinc-900">
          &larr; Back
        </Link>
        <h1 className="text-3xl font-bold font-mono">{experiment.experiment_id}</h1>
        <Badge
          variant={
            experiment.status === "completed"
              ? "success"
              : experiment.status === "running"
                ? "warning"
                : experiment.status === "failed"
                  ? "destructive"
                  : "secondary"
          }
        >
          {experiment.status}
        </Badge>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-500">Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <p>
              <span className="text-zinc-500">Architecture:</span>{" "}
              <span className="capitalize">{experiment.architecture.replace("_", " ")}</span>
            </p>
            <p>
              <span className="text-zinc-500">Benchmark:</span>{" "}
              <span className="uppercase">{experiment.benchmark}</span>
            </p>
            <p>
              <span className="text-zinc-500">SLM:</span> {experiment.slm}
            </p>
            <p>
              <span className="text-zinc-500">LLM:</span> {experiment.llm}
            </p>
            <p>
              <span className="text-zinc-500">Samples:</span> {experiment.n_samples}
            </p>
            <p>
              <span className="text-zinc-500">Created:</span> {formatDate(experiment.created_at)}
            </p>
            {experiment.completed_at && (
              <p>
                <span className="text-zinc-500">Completed:</span>{" "}
                {formatDate(experiment.completed_at)}
              </p>
            )}
          </CardContent>
        </Card>

        {experiment.metrics && (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-zinc-500">Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                {Object.entries(experiment.metrics).map(([key, value]) => (
                  <p key={key}>
                    <span className="text-zinc-500">{key}:</span>{" "}
                    {key.includes("cost") ? formatCost(value) : key.includes("ratio") || key.includes("accuracy") ? formatPercent(value) : value.toFixed(4)}
                  </p>
                ))}
              </CardContent>
            </Card>

            {experiment.metrics.eats_score != null && (
              <EATSGauge score={experiment.metrics.eats_score} />
            )}
          </>
        )}
      </div>

      {isActive && (
        <LiveProgress experimentId={experiment.experiment_id} enabled={isActive} />
      )}

      {experiment.error && (
        <Card>
          <CardContent className="py-4">
            <p className="font-medium text-red-700">Error</p>
            <p className="text-sm text-red-600">{experiment.error}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
