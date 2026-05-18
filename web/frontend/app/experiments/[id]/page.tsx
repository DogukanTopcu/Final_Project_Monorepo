"use client";

import Link from "next/link";
import { Fragment, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EATSGauge } from "@/components/EATSGauge";
import { LiveProgress } from "@/components/LiveProgress";
import { useExperiment, useResult } from "@/hooks/useExperiments";
import type { ResultSample } from "@/types";
import {
  formatCost,
  formatDate,
  formatDecimal,
  formatDurationMs,
  formatMetricLabel,
  formatMetricValue,
  formatNumber,
  formatPercent,
} from "@/lib/utils";

function valueOrDash(value: number | string | null | undefined): string {
  if (value == null) {
    return "—";
  }
  if (typeof value === "number") {
    return formatDecimal(value);
  }
  return value;
}

export default function ExperimentDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const { data: experiment, isLoading: experimentLoading } = useExperiment(id);
  const { data: resultDetail, isLoading: resultLoading } = useResult(id);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  if (experimentLoading && resultLoading) {
    return <p className="text-zinc-500">Loading experiment...</p>;
  }

  if (!experiment && !resultDetail) {
    return <p className="text-red-600">Experiment not found.</p>;
  }

  const isActive =
    experiment?.status === "running" || experiment?.status === "queued";
  const metrics = resultDetail?.metrics ?? experiment?.metrics ?? null;
  const samples = resultDetail?.samples ?? [];
  const config = resultDetail?.config ?? experiment?.config_overrides ?? {};
  const confidenceThreshold = Number(
    config.confidence_threshold ?? experiment?.config_overrides?.confidence_threshold ?? 0.7,
  );
  const llmLabel = experiment?.llm ?? String(config.llm ?? "unknown");
  const slmLabel = experiment?.slm ?? String(config.slm ?? "unknown");
  const nEscalated = Math.round(metrics?.n_escalated ?? 0);
  const llmCallRatio = metrics?.llm_call_ratio ?? 0;
  const hasFallbackCalls = llmCallRatio > 0 || nEscalated > 0;
  const canExplainFallbackOutcome = !isActive && metrics != null;
  const displayedMetricKeys = [
    "accuracy",
    "llm_call_ratio",
    "avg_latency_ms",
    "latency_p50_ms",
    "latency_p95_ms",
    "total_cost_usd",
    "total_tokens",
    "eats_score",
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/experiments" className="text-zinc-500 hover:text-zinc-900">
          &larr; Back
        </Link>
        <h1 className="text-3xl font-bold font-mono">
          {experiment?.experiment_id ?? resultDetail?.experiment_id}
        </h1>
        {experiment && (
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
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-500">Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <p>
              <span className="text-zinc-500">Architecture:</span>{" "}
              <span className="capitalize">
                {(experiment?.architecture ?? resultDetail?.architecture ?? "unknown").replace("_", " ")}
              </span>
            </p>
            <p>
              <span className="text-zinc-500">Benchmark:</span>{" "}
              <span className="uppercase">{experiment?.benchmark ?? resultDetail?.benchmark}</span>
            </p>
            <p>
              <span className="text-zinc-500">SLM:</span> {slmLabel}
            </p>
            <p>
              <span className="text-zinc-500">LLM:</span> {llmLabel}
            </p>
            <p>
              <span className="text-zinc-500">Samples:</span>{" "}
              {experiment?.n_samples ?? valueOrDash(metrics?.n_total)}
            </p>
            <p>
              <span className="text-zinc-500">Threshold:</span>{" "}
              {formatPercent(confidenceThreshold)}
            </p>
            <p>
              <span className="text-zinc-500">Created:</span>{" "}
              {formatDate(experiment?.created_at ?? resultDetail?.created_at ?? "")}
            </p>
            {experiment?.completed_at && (
              <p>
                <span className="text-zinc-500">Completed:</span>{" "}
                {formatDate(experiment.completed_at)}
              </p>
            )}
          </CardContent>
        </Card>

        {metrics && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-zinc-500">Readable Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              {displayedMetricKeys
                .filter((key) => metrics[key] != null)
                .map((key) => (
                  <p key={key}>
                    <span className="text-zinc-500">{formatMetricLabel(key)}:</span>{" "}
                    {formatMetricValue(key, metrics[key])}
                  </p>
                ))}
            </CardContent>
          </Card>
        )}

        {metrics?.eats_score != null && (
          <EATSGauge score={metrics.eats_score} />
        )}
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-500">Routing Explanation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-zinc-700">
          <p>
            Routing first queries the local SLM. {llmLabel} is called only when SLM
            confidence is below {formatPercent(confidenceThreshold)}.
          </p>
          {!canExplainFallbackOutcome ? (
            <p className="rounded-md bg-zinc-100 px-3 py-2 text-zinc-700">
              This run is still in progress. Fallback usage summary will be finalized when the experiment completes.
            </p>
          ) : !hasFallbackCalls ? (
            <p className="rounded-md bg-green-50 px-3 py-2 text-green-700">
              No fallback calls were made in this run; all samples were answered locally by the SLM.
            </p>
          ) : (
            <p className="rounded-md bg-amber-50 px-3 py-2 text-amber-800">
              Fallback was used on {formatNumber(nEscalated)} sample(s), which is {formatPercent(metrics?.escalation_rate ?? llmCallRatio)} of the run.
            </p>
          )}
        </CardContent>
      </Card>

      {metrics && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-zinc-500">Escalated Samples</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {formatNumber(Math.round(metrics.n_escalated ?? 0))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-zinc-500">Escalation Rate</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {formatPercent(metrics.escalation_rate ?? llmCallRatio)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-zinc-500">Fallback Cost</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {formatCost(metrics.total_cost_usd ?? 0)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-zinc-500">Avg SLM Confidence</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {formatPercent(metrics.avg_slm_confidence ?? 0)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-zinc-500">SLM-only Samples</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {formatNumber(Math.round(metrics.n_slm_only ?? 0))}
            </CardContent>
          </Card>
        </div>
      )}

      {isActive && experiment && (
        <LiveProgress experimentId={experiment.experiment_id} enabled={isActive} />
      )}

      <Card>
        <CardHeader>
          <CardTitle>Sample Audit Trail</CardTitle>
        </CardHeader>
        <CardContent>
          {!samples.length ? (
            <p className="text-sm text-zinc-500">
              Sample-level routing audit is not available for this result yet.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-zinc-200 text-zinc-500">
                    <th className="pb-3 pr-4 font-medium">Query</th>
                    <th className="pb-3 pr-4 font-medium">Correct</th>
                    <th className="pb-3 pr-4 font-medium">Escalated</th>
                    <th className="pb-3 pr-4 font-medium">Final Model</th>
                    <th className="pb-3 pr-4 font-medium">SLM Confidence</th>
                    <th className="pb-3 pr-4 font-medium">Latency</th>
                    <th className="pb-3 pr-4 font-medium">Cost</th>
                    <th className="pb-3 font-medium">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {samples.map((sample) => {
                    const isExpanded = !!expanded[sample.query_id];
                    const canExpand = !!sample.escalated;
                    return (
                      <Fragment key={sample.query_id}>
                        <tr
                          className="border-b border-zinc-100 align-top hover:bg-zinc-50"
                        >
                          <td className="py-3 pr-4 font-mono">{sample.query_id}</td>
                          <td className="py-3 pr-4">
                            <Badge variant={sample.correct ? "success" : "destructive"}>
                              {sample.correct ? "correct" : "wrong"}
                            </Badge>
                          </td>
                          <td className="py-3 pr-4">
                            <Badge variant={sample.escalated ? "warning" : "secondary"}>
                              {sample.escalated ? "yes" : "no"}
                            </Badge>
                          </td>
                          <td className="py-3 pr-4">{valueOrDash(sample.final_model_id)}</td>
                          <td className="py-3 pr-4">
                            {sample.slm_confidence != null ? formatPercent(sample.slm_confidence) : "—"}
                          </td>
                          <td className="py-3 pr-4">
                            {sample.latency_ms != null ? formatDurationMs(sample.latency_ms) : "—"}
                          </td>
                          <td className="py-3 pr-4">
                            {sample.cost_usd != null ? formatCost(sample.cost_usd) : "—"}
                          </td>
                          <td className="py-3">
                            {canExpand ? (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() =>
                                  setExpanded((prev) => ({
                                    ...prev,
                                    [sample.query_id]: !prev[sample.query_id],
                                  }))
                                }
                              >
                                {isExpanded ? "Hide" : "Show"}
                              </Button>
                            ) : (
                              <span className="text-zinc-400">—</span>
                            )}
                          </td>
                        </tr>
                        {isExpanded && (
                          <tr className="border-b border-zinc-100 bg-zinc-50/70">
                            <td colSpan={8} className="px-4 py-4">
                              <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
                                <div>
                                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    Prompt
                                  </p>
                                  <pre className="whitespace-pre-wrap rounded-md bg-white p-3 text-xs text-zinc-700">
                                    {sample.prompt_text ?? "Not available"}
                                  </pre>
                                </div>
                                <div>
                                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    SLM Answer
                                  </p>
                                  <pre className="whitespace-pre-wrap rounded-md bg-white p-3 text-xs text-zinc-700">
                                    {sample.slm_text ?? "Not available"}
                                  </pre>
                                </div>
                                <div>
                                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    Final Answer
                                  </p>
                                  <pre className="whitespace-pre-wrap rounded-md bg-white p-3 text-xs text-zinc-700">
                                    {sample.final_text ?? "Not available"}
                                  </pre>
                                  <p className="mt-2 text-xs text-zinc-500">
                                    Confidence {sample.slm_confidence != null ? formatPercent(sample.slm_confidence) : "—"} vs threshold{" "}
                                    {sample.confidence_threshold != null ? formatPercent(sample.confidence_threshold) : "—"}
                                  </p>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {experiment?.error && (
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
