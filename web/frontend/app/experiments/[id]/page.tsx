"use client";

import Link from "next/link";
import { Fragment, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EATSGauge } from "@/components/EATSGauge";
import { LiveProgress } from "@/components/LiveProgress";
import { useExperiment, useResult } from "@/hooks/useExperiments";
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

type Tab = "overview" | "metrics" | "samples" | "inference" | "config";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "metrics", label: "Metrics" },
  { id: "samples", label: "Samples" },
  { id: "inference", label: "Inference steps" },
  { id: "config", label: "Config" },
];

function valueOrDash(value: number | string | null | undefined): string {
  if (value == null) return "—";
  if (typeof value === "number") return formatDecimal(value);
  return value;
}

function formatTokenBudget(value: number | null | undefined): string {
  if (value == null || value <= 0) return "auto";
  return formatNumber(value);
}

export default function ExperimentDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const { data: experiment, isLoading: experimentLoading } = useExperiment(id);
  const { data: resultDetail, isLoading: resultLoading } = useResult(id);
  const [tab, setTab] = useState<Tab>("overview");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  if (experimentLoading && resultLoading) {
    return <p className="text-zinc-500">Loading experiment…</p>;
  }
  if (!experiment && !resultDetail) {
    return <p className="text-red-600">Experiment not found.</p>;
  }

  const architecture = String(
    experiment?.architecture ?? resultDetail?.architecture ?? "unknown",
  );
  const benchmark = String(experiment?.benchmark ?? resultDetail?.benchmark ?? "—");
  const slm = experiment?.slm ?? (resultDetail?.config?.slm as string | undefined) ?? null;
  const llm = experiment?.llm ?? (resultDetail?.config?.llm as string | undefined) ?? null;
  const ensembleSlms =
    experiment?.ensemble_slms ??
    ((resultDetail?.config?.ensemble_slms as string[] | undefined) ?? []);

  const isActive = experiment?.status === "running" || experiment?.status === "queued";
  const metrics = resultDetail?.metrics ?? experiment?.metrics ?? null;
  const samples = resultDetail?.samples ?? [];
  const config = resultDetail?.config ?? experiment?.config_overrides ?? {};
  const confidenceThreshold = Number(config.confidence_threshold ?? 0.7);
  const slmTemperature = Number(config.slm_temperature ?? 0);
  const llmTemperature = Number(config.llm_temperature ?? 0);
  const slmMaxTokens = Number(config.slm_max_tokens ?? 0);
  const llmMaxTokens = Number(config.llm_max_tokens ?? 0);
  const nEscalated = Math.round(metrics?.n_escalated ?? 0);
  const llmCallRatio = metrics?.llm_call_ratio ?? 0;
  const hasFallbackCalls = llmCallRatio > 0 || nEscalated > 0;

  const orderedMetricKeys = [
    "accuracy",
    "llm_call_ratio",
    "avg_latency_ms",
    "latency_p50_ms",
    "latency_p95_ms",
    "total_cost_usd",
    "total_api_cost_usd",
    "total_infra_cost_usd",
    "total_energy_kwh",
    "total_co2_g",
    "total_tokens",
    "eats_score",
    "n_total",
    "n_correct",
    "n_escalated",
    "n_slm_only",
    "escalation_rate",
    "avg_slm_confidence",
  ];

  const allMetricKeys = metrics
    ? [...orderedMetricKeys.filter((k) => metrics[k] != null),
       ...Object.keys(metrics).filter((k) => !orderedMetricKeys.includes(k))]
    : [];

  function architectureExplainer() {
    if (architecture === "monolithic") {
      return (
        <p>
          Every query was answered directly by <strong>{llm}</strong>. This is the
          accuracy / cost ceiling baseline.
        </p>
      );
    }
    if (architecture === "routing") {
      return (
        <p>
          The SLM <strong>{slm}</strong> answers first; the run only escalates to{" "}
          <strong>{llm}</strong> when SLM confidence is below {formatPercent(confidenceThreshold)}.
        </p>
      );
    }
    if (architecture === "multi_agent") {
      return (
        <p>
          Proponent / opponent debate flow between SLM <strong>{slm}</strong> and LLM{" "}
          <strong>{llm}</strong>. The arbitrator decides the final answer.
        </p>
      );
    }
    if (architecture === "ensemble") {
      return (
        <p>
          {ensembleSlms.length} SLMs voted: <strong>{ensembleSlms.join(", ")}</strong>
          {config.llm_tiebreak ? (
            <> · tiebreak <strong>{llm}</strong> was called only when no majority emerged.</>
          ) : (
            <> · no LLM tiebreak.</>
          )}
        </p>
      );
    }
    if (architecture === "speculative") {
      return (
        <p>
          Drafter <strong>{slm}</strong> proposed tokens; verifier <strong>{llm}</strong>{" "}
          accepted or rewrote them based on the acceptance threshold.
        </p>
      );
    }
    if (architecture === "multi_agent_crew") {
      return (
        <p>
          Domain-routed crew of three specialist SLMs (reasoning / code / factual). The crew
          self-classifies each query and routes it to the best-fit agent.
        </p>
      );
    }
    return <p>Architecture: {architecture}.</p>;
  }

  // Inference steps: pulled from samples[*].inference_steps (each sample is a
  // list of per-role calls — model_id, latency_ms, tokens, cost).
  const inferenceSteps = samples.flatMap((s, sIdx) =>
    (s.inference_steps ?? []).map((step, idx) => ({
      sampleIdx: sIdx,
      stepIdx: idx,
      queryId: s.query_id,
      role: String(step.role ?? "?"),
      model: String(step.model_id ?? "?"),
      latency: Number(step.latency_ms ?? 0),
      tokensIn: Number(step.input_tokens ?? 0),
      tokensOut: Number(step.output_tokens ?? 0),
      cost: Number(step.api_cost_usd ?? 0),
    })),
  );
  const stepsByRole = new Map<string, typeof inferenceSteps>();
  for (const step of inferenceSteps) {
    if (!stepsByRole.has(step.role)) stepsByRole.set(step.role, []);
    stepsByRole.get(step.role)!.push(step);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <Link href="/experiments" className="text-sm text-zinc-500 hover:text-zinc-900">
          ← Back
        </Link>
        <h1 className="font-mono text-2xl font-bold">
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
        <Badge variant="outline" className="capitalize">{architecture.replace(/_/g, " ")}</Badge>
        <Badge variant="secondary" className="uppercase">{benchmark}</Badge>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-zinc-200">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-3 py-2 text-sm font-medium transition ${
              tab === t.id
                ? "border-b-2 border-zinc-900 text-zinc-900"
                : "text-zinc-500 hover:text-zinc-900"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-zinc-500">Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                <p>
                  <span className="text-zinc-500">Architecture:</span>{" "}
                  <span className="capitalize">{architecture.replace(/_/g, " ")}</span>
                </p>
                <p>
                  <span className="text-zinc-500">Benchmark:</span>{" "}
                  <span className="uppercase">{benchmark}</span>
                </p>
                {architecture === "ensemble" ? (
                  <p>
                    <span className="text-zinc-500">Ensemble SLMs:</span>{" "}
                    {ensembleSlms.length ? ensembleSlms.join(", ") : "—"}
                  </p>
                ) : (
                  <p>
                    <span className="text-zinc-500">SLM:</span> {slm ?? "—"}
                  </p>
                )}
                <p>
                  <span className="text-zinc-500">LLM:</span> {llm ?? "—"}
                </p>
                <p>
                  <span className="text-zinc-500">Samples:</span>{" "}
                  {experiment?.n_samples ?? valueOrDash(metrics?.n_total)}
                </p>
                {architecture === "routing" && (
                  <p>
                    <span className="text-zinc-500">Threshold:</span>{" "}
                    {formatPercent(confidenceThreshold)}
                  </p>
                )}
                <p>
                  <span className="text-zinc-500">SLM temp / max tokens:</span>{" "}
                  {formatDecimal(slmTemperature)} / {formatTokenBudget(slmMaxTokens)}
                </p>
                <p>
                  <span className="text-zinc-500">LLM temp / max tokens:</span>{" "}
                  {formatDecimal(llmTemperature)} / {formatTokenBudget(llmMaxTokens)}
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
                  <CardTitle className="text-sm text-zinc-500">Headline metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-1 text-sm">
                  {["accuracy", "llm_call_ratio", "avg_latency_ms", "total_cost_usd", "total_energy_kwh", "eats_score"]
                    .filter((k) => metrics[k] != null)
                    .map((k) => (
                      <p key={k}>
                        <span className="text-zinc-500">{formatMetricLabel(k)}:</span>{" "}
                        {formatMetricValue(k, metrics[k])}
                      </p>
                    ))}
                </CardContent>
              </Card>
            )}

            {metrics?.eats_score != null && <EATSGauge score={metrics.eats_score} />}
          </div>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-zinc-500">How it ran</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-zinc-700">
              {architectureExplainer()}
              {architecture === "routing" && metrics && (
                !hasFallbackCalls ? (
                  <p className="rounded-md bg-green-50 px-3 py-2 text-green-700">
                    No escalation: every sample was answered locally by the SLM.
                  </p>
                ) : (
                  <p className="rounded-md bg-amber-50 px-3 py-2 text-amber-800">
                    Escalated {formatNumber(nEscalated)} sample(s) —{" "}
                    {formatPercent(metrics.escalation_rate ?? llmCallRatio)} of the run.
                  </p>
                )
              )}
            </CardContent>
          </Card>

          {isActive && experiment && (
            <LiveProgress experimentId={experiment.experiment_id} enabled={isActive} />
          )}

          {experiment?.error && (
            <Card>
              <CardContent className="py-4">
                <p className="font-medium text-red-700">Error</p>
                <p className="text-sm text-red-600">{experiment.error}</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {tab === "metrics" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">All metrics</CardTitle>
          </CardHeader>
          <CardContent>
            {!metrics ? (
              <p className="text-sm text-zinc-500">Metrics not yet available.</p>
            ) : (
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                {allMetricKeys.map((k) => (
                  <div key={k} className="rounded-md border border-zinc-100 bg-white p-3">
                    <div className="text-xs text-zinc-500">{formatMetricLabel(k)}</div>
                    <div className="text-lg font-semibold text-zinc-900">
                      {formatMetricValue(k, metrics[k])}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "samples" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Sample audit trail</CardTitle>
          </CardHeader>
          <CardContent>
            {!samples.length ? (
              <p className="text-sm text-zinc-500">
                Sample-level details are not available for this run yet.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-zinc-200 text-xs uppercase tracking-wider text-zinc-500">
                      <th className="pb-3 pr-4">Query</th>
                      <th className="pb-3 pr-4">Correct</th>
                      <th className="pb-3 pr-4">Used LLM</th>
                      <th className="pb-3 pr-4">Final model</th>
                      <th className="pb-3 pr-4">SLM conf.</th>
                      <th className="pb-3 pr-4">Latency</th>
                      <th className="pb-3 pr-4">Cost</th>
                      <th className="pb-3"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {samples.map((sample) => {
                      const isExpanded = !!expanded[sample.query_id];
                      const canExpand =
                        !!sample.prompt_text ||
                        !!sample.slm_text ||
                        !!sample.final_text ||
                        (sample.inference_steps?.length ?? 0) > 0;
                      return (
                        <Fragment key={sample.query_id}>
                          <tr className="border-b border-zinc-100 align-top hover:bg-zinc-50">
                            <td className="py-3 pr-4 font-mono">{sample.query_id}</td>
                            <td className="py-3 pr-4">
                              <Badge variant={sample.correct ? "success" : "destructive"}>
                                {sample.correct ? "correct" : "wrong"}
                              </Badge>
                            </td>
                            <td className="py-3 pr-4">
                              <Badge
                                variant={
                                  (sample.llm_calls ?? 0) > 0 || sample.escalated
                                    ? "warning"
                                    : "secondary"
                                }
                              >
                                {(sample.llm_calls ?? 0) > 0 || sample.escalated ? "yes" : "no"}
                              </Badge>
                            </td>
                            <td className="py-3 pr-4">{valueOrDash(sample.final_model_id)}</td>
                            <td className="py-3 pr-4">
                              {sample.slm_confidence != null
                                ? formatPercent(sample.slm_confidence)
                                : "—"}
                            </td>
                            <td className="py-3 pr-4">
                              {sample.latency_ms != null
                                ? formatDurationMs(sample.latency_ms)
                                : "—"}
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
                                      SLM answer
                                    </p>
                                    <pre className="whitespace-pre-wrap rounded-md bg-white p-3 text-xs text-zinc-700">
                                      {sample.slm_text ?? "Not available"}
                                    </pre>
                                  </div>
                                  <div>
                                    <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                      Final answer
                                    </p>
                                    <pre className="whitespace-pre-wrap rounded-md bg-white p-3 text-xs text-zinc-700">
                                      {sample.final_text ?? "Not available"}
                                    </pre>
                                  </div>
                                </div>
                                {(sample.inference_steps?.length ?? 0) > 0 && (
                                  <div className="mt-3">
                                    <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                      Inference steps
                                    </p>
                                    <table className="w-full text-xs">
                                      <thead>
                                        <tr className="text-left text-zinc-500">
                                          <th className="pb-1 pr-2">Role</th>
                                          <th className="pb-1 pr-2">Model</th>
                                          <th className="pb-1 pr-2">Latency</th>
                                          <th className="pb-1 pr-2">Tokens in/out</th>
                                          <th className="pb-1">Cost</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {(sample.inference_steps ?? []).map((step, idx) => (
                                          <tr key={idx} className="border-t border-zinc-100">
                                            <td className="py-1 pr-2">{String(step.role ?? "—")}</td>
                                            <td className="py-1 pr-2 font-mono">
                                              {String(step.model_id ?? "—")}
                                            </td>
                                            <td className="py-1 pr-2">
                                              {formatDurationMs(Number(step.latency_ms ?? 0))}
                                            </td>
                                            <td className="py-1 pr-2">
                                              {formatNumber(Number(step.input_tokens ?? 0))} /{" "}
                                              {formatNumber(Number(step.output_tokens ?? 0))}
                                            </td>
                                            <td className="py-1">
                                              {formatCost(Number(step.api_cost_usd ?? 0))}
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                )}
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
      )}

      {tab === "inference" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Inference steps by role</CardTitle>
          </CardHeader>
          <CardContent>
            {inferenceSteps.length === 0 ? (
              <p className="text-sm text-zinc-500">
                No inference step trace available for this run.
              </p>
            ) : (
              <div className="space-y-4">
                {Array.from(stepsByRole.entries()).map(([role, steps]) => {
                  const totalLat = steps.reduce((s, x) => s + x.latency, 0);
                  const totalIn = steps.reduce((s, x) => s + x.tokensIn, 0);
                  const totalOut = steps.reduce((s, x) => s + x.tokensOut, 0);
                  const totalCost = steps.reduce((s, x) => s + x.cost, 0);
                  return (
                    <div key={role} className="rounded-md border border-zinc-200 bg-white p-3">
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <Badge variant="secondary" className="text-[11px]">
                          {role}
                        </Badge>
                        <span className="text-xs text-zinc-500">{steps.length} calls</span>
                        <span className="text-xs text-zinc-500">
                          total {formatDurationMs(totalLat)} · {totalIn}/{totalOut} tokens ·{" "}
                          {formatCost(totalCost)}
                        </span>
                      </div>
                      <div className="text-xs text-zinc-500">
                        Models:{" "}
                        {Array.from(new Set(steps.map((s) => s.model))).join(", ")}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "config" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Raw configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="overflow-x-auto rounded-md bg-zinc-50 p-3 text-xs text-zinc-800">
              {JSON.stringify(config, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
