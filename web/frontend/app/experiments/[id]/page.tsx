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
import type {
  EnsembleMemberResponse,
  ResultSample,
  ResultSampleInferenceStep,
} from "@/types";

type Tab = "overview" | "metrics" | "samples" | "inference" | "config";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "metrics", label: "Metrics" },
  { id: "samples", label: "Samples" },
  { id: "inference", label: "Inference steps" },
  { id: "config", label: "Config" },
];

const CORE_TEXT_FIELDS = [
  "query_text",
  "prompt_text",
  "slm_text",
  "final_text",
  "predicted",
  "ground_truth",
] as const;

const SAMPLE_DETAIL_FIELDS = [
  "correct",
  "llm_calls",
  "used_llm",
  "escalated",
  "confidence",
  "slm_confidence",
  "confidence_threshold",
  "final_model_id",
  "latency_ms",
  "cost_usd",
  "api_cost_usd",
  "infra_cost_usd",
  "energy_kwh",
  "co2_g",
  "gpu_power_w",
  "slm_latency_ms",
  "llm_latency_ms",
  "slm_input_tokens",
  "slm_output_tokens",
  "llm_input_tokens",
  "llm_output_tokens",
  "slm_cost_usd",
  "llm_cost_usd",
] as const;

type ScalarValue = string | number | boolean | null | undefined;

function valueOrDash(value: number | string | null | undefined): string {
  if (value == null) return "—";
  if (typeof value === "number") return formatDecimal(value);
  return value;
}

function formatTokenBudget(value: number | null | undefined): string {
  if (value == null || value <= 0) return "auto";
  return formatNumber(value);
}

function formatFieldLabel(key: string): string {
  const labels: Record<string, string> = {
    query_id: "Query ID",
    query_text: "Query text",
    prompt_text: "Prompt",
    slm_text: "SLM answer",
    final_text: "Final answer",
    predicted: "Predicted",
    ground_truth: "Ground truth",
    llm_calls: "LLM calls",
    used_llm: "Used LLM",
    escalated: "Escalated",
    final_model_id: "Final model",
    slm_confidence: "SLM confidence",
    confidence_threshold: "Confidence threshold",
    latency_ms: "Latency",
    cost_usd: "Total cost",
    api_cost_usd: "API cost",
    infra_cost_usd: "Infra cost",
    energy_kwh: "Energy",
    co2_g: "CO2",
    gpu_power_w: "GPU power",
    slm_latency_ms: "SLM latency",
    llm_latency_ms: "LLM latency",
    slm_input_tokens: "SLM input tokens",
    slm_output_tokens: "SLM output tokens",
    llm_input_tokens: "LLM input tokens",
    llm_output_tokens: "LLM output tokens",
    slm_cost_usd: "SLM cost",
    llm_cost_usd: "LLM cost",
    resource_estimate: "Resource estimate",
    inference_steps: "Inference steps",
    model_id: "Model",
    host_label: "Host",
    duration_s: "Duration",
    input_tokens: "Input tokens",
    output_tokens: "Output tokens",
    role: "Role",
  };
  if (labels[key]) return labels[key];

  return key
    .split("_")
    .map((part) => {
      const upper = part.toUpperCase();
      if (upper === "LLM" || upper === "SLM" || upper === "API" || upper === "CO2") {
        return upper;
      }
      if (upper === "MS" || upper === "USD" || upper === "KWH") {
        return upper;
      }
      return part.charAt(0).toUpperCase() + part.slice(1);
    })
    .join(" ");
}

function isScalarValue(value: unknown): value is string | number | boolean | null | undefined {
  return (
    value == null ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  );
}

function formatScalarValue(value: ScalarValue, key?: string): string {
  if (value == null) return "—";
  if (typeof value === "boolean") return value ? "yes" : "no";
  if (typeof value === "string") return value || "—";
  if (Number.isNaN(value)) return "—";

  if (key?.includes("cost")) return formatCost(value);
  if (key?.endsWith("_ms")) return formatDurationMs(value);
  if (key === "duration_s") return `${formatDecimal(value, 3)}s`;
  if (key?.includes("confidence") && value >= 0 && value <= 1) {
    return formatPercent(value);
  }
  if (key?.includes("energy")) return `${formatDecimal(value, 6)} kWh`;
  if (key?.includes("co2")) return `${formatDecimal(value, 4)} g`;
  if (key?.includes("power")) return `${formatDecimal(value, 1)} W`;
  if (key?.includes("tokens") || key === "llm_calls") {
    return formatNumber(Math.round(value));
  }
  if (Number.isInteger(value)) return formatNumber(value);
  return formatDecimal(value, 4);
}

function stringifyJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

function getSampleTextValue(sample: ResultSample, field: (typeof CORE_TEXT_FIELDS)[number]): string {
  const value = sample[field];
  if (typeof value !== "string") return "Not available";
  const trimmed = value.trim();
  return trimmed || "Not available";
}

function getSampleQuestionPreview(sample: ResultSample): string {
  const promptText =
    typeof sample.prompt_text === "string" ? sample.prompt_text.trim() : "";
  if (promptText) return promptText;

  const queryText =
    typeof sample.query_text === "string" ? sample.query_text.trim() : "";
  const queryChoices = Array.isArray(sample.query_choices)
    ? sample.query_choices.filter((choice): choice is string => typeof choice === "string")
    : [];
  if (queryText && queryChoices.length) {
    const labeledChoices = queryChoices.map((choice, idx) => {
      const label = String.fromCharCode(65 + idx);
      return `${label}. ${choice}`;
    });
    return [queryText, ...labeledChoices].join("\n");
  }
  if (queryText) return queryText;

  return "Not available";
}

function getSampleDetailEntries(sample: ResultSample): Array<[string, ScalarValue]> {
  const excluded = new Set<string>([
    "query_id",
    ...CORE_TEXT_FIELDS,
    "resource_estimate",
    "inference_steps",
  ]);
  const preferredKeys = new Set<string>();
  const entries: Array<[string, ScalarValue]> = [];

  for (const key of SAMPLE_DETAIL_FIELDS) {
    const value = sample[key];
    if (value !== undefined && isScalarValue(value)) {
      preferredKeys.add(key);
      entries.push([key, value]);
    }
  }

  const extraEntries = Object.entries(sample)
    .filter(
      ([key, value]) =>
        !excluded.has(key) && !preferredKeys.has(key) && isScalarValue(value),
    )
    .map(([key, value]) => [key, value as ScalarValue] as [string, ScalarValue])
    .sort(([a], [b]) => a.localeCompare(b));

  return [...entries, ...extraEntries];
}

function getStepEntries(step: ResultSampleInferenceStep): Array<[string, unknown]> {
  return Object.entries(step).sort(([a], [b]) => a.localeCompare(b));
}

function getEnsembleMemberResponses(sample: ResultSample): EnsembleMemberResponse[] {
  return Array.isArray(sample.ensemble_member_responses)
    ? sample.ensemble_member_responses
    : [];
}

export default function ExperimentDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const { data: experiment, isLoading: experimentLoading } = useExperiment(id);
  const { data: resultDetail, isLoading: resultLoading } = useResult(id, {
    expectedSamples: experiment?.n_samples ?? null,
  });
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
    ? [
        ...orderedMetricKeys.filter((k) => metrics[k] != null),
        ...Object.keys(metrics).filter((k) => !orderedMetricKeys.includes(k)),
      ]
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
        <Badge variant="outline" className="capitalize">
          {architecture.replace(/_/g, " ")}
        </Badge>
        <Badge variant="secondary" className="uppercase">
          {benchmark}
        </Badge>
      </div>

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
                  {[
                    "accuracy",
                    "llm_call_ratio",
                    "avg_latency_ms",
                    "total_cost_usd",
                    "total_energy_kwh",
                    "eats_score",
                  ]
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
                <>
                  {!hasFallbackCalls ? (
                    <p className="rounded-md bg-green-50 px-3 py-2 text-green-700">
                      No escalation: every sample was answered locally by the SLM.
                    </p>
                  ) : (
                    <p className="rounded-md bg-amber-50 px-3 py-2 text-amber-800">
                      Escalated {formatNumber(nEscalated)} sample(s) —{" "}
                      {formatPercent(metrics.escalation_rate ?? llmCallRatio)} of the run.
                    </p>
                  )}
                </>
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
              <div className="space-y-3">
                {samples.map((sample) => {
                  const isExpanded = !!expanded[sample.query_id];
                  const detailEntries = getSampleDetailEntries(sample);
                  const memberResponses = getEnsembleMemberResponses(sample);
                  return (
                    <Fragment key={sample.query_id}>
                      <div className="rounded-lg border border-zinc-200 bg-white">
                        <div className="space-y-3 px-4 py-3">
                          <div className="flex flex-wrap items-start justify-between gap-3">
                            <div className="min-w-0 flex-1">
                              <div className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">
                                Sample
                              </div>
                              <div className="truncate font-mono text-sm text-zinc-900">
                                {sample.query_id}
                              </div>
                              <div className="mt-2 text-[11px] font-semibold uppercase tracking-wide text-zinc-500">
                                Question
                              </div>
                              <div className="mt-1 whitespace-pre-wrap break-words text-sm leading-5 text-zinc-700">
                                {getSampleQuestionPreview(sample)}
                              </div>
                            </div>
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
                          </div>

                          <div className="grid grid-cols-2 gap-2 md:grid-cols-3 xl:grid-cols-6">
                            <div className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2">
                              <div className="text-[11px] uppercase tracking-wide text-zinc-500">
                                Correct
                              </div>
                              <div className="mt-1">
                                <Badge variant={sample.correct ? "success" : "destructive"}>
                                  {sample.correct ? "correct" : "wrong"}
                                </Badge>
                              </div>
                            </div>
                            <div className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2">
                              <div className="text-[11px] uppercase tracking-wide text-zinc-500">
                                Used LLM
                              </div>
                              <div className="mt-1">
                                <Badge
                                  variant={
                                    (sample.llm_calls ?? 0) > 0 || sample.escalated
                                      ? "warning"
                                      : "secondary"
                                  }
                                >
                                  {(sample.llm_calls ?? 0) > 0 || sample.escalated ? "yes" : "no"}
                                </Badge>
                              </div>
                            </div>
                            <div className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2">
                              <div className="text-[11px] uppercase tracking-wide text-zinc-500">
                                Final model
                              </div>
                              <div className="mt-1 break-all text-sm font-medium text-zinc-900">
                                {valueOrDash(sample.final_model_id)}
                              </div>
                            </div>
                            <div className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2">
                              <div className="text-[11px] uppercase tracking-wide text-zinc-500">
                                SLM conf.
                              </div>
                              <div className="mt-1 text-sm font-medium text-zinc-900">
                                {sample.slm_confidence != null
                                  ? formatPercent(sample.slm_confidence)
                                  : "—"}
                              </div>
                            </div>
                            <div className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2">
                              <div className="text-[11px] uppercase tracking-wide text-zinc-500">
                                Latency
                              </div>
                              <div className="mt-1 text-sm font-medium text-zinc-900">
                                {sample.latency_ms != null
                                  ? formatDurationMs(sample.latency_ms)
                                  : "—"}
                              </div>
                            </div>
                            <div className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2">
                              <div className="text-[11px] uppercase tracking-wide text-zinc-500">
                                Cost
                              </div>
                              <div className="mt-1 text-sm font-medium text-zinc-900">
                                {sample.cost_usd != null ? formatCost(sample.cost_usd) : "—"}
                              </div>
                            </div>
                          </div>
                        </div>

                        {isExpanded && (
                          <div className="border-t border-zinc-200 bg-zinc-50/70 px-4 py-4">
                            <div className="space-y-4">
                                  {architecture === "ensemble" && (
                                    <section className="space-y-3">
                                      <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                        Ensemble decision
                                      </p>
                                      <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                                        <div className="rounded-md border border-zinc-200 bg-white px-3 py-2">
                                          <div className="text-xs text-zinc-500">Voting method</div>
                                          <div className="mt-1 text-sm font-medium text-zinc-900">
                                            {typeof sample.voting_method === "string"
                                              ? sample.voting_method
                                              : "—"}
                                          </div>
                                        </div>
                                        <div className="rounded-md border border-zinc-200 bg-white px-3 py-2">
                                          <div className="text-xs text-zinc-500">Vote counts</div>
                                          <div className="mt-1 break-words text-sm font-medium text-zinc-900">
                                            {sample.vote_counts &&
                                            typeof sample.vote_counts === "object" &&
                                            Object.keys(sample.vote_counts).length
                                              ? Object.entries(sample.vote_counts)
                                                  .map(([answer, count]) => `${answer}: ${count}`)
                                                  .join(" · ")
                                              : "—"}
                                          </div>
                                        </div>
                                        <div className="rounded-md border border-zinc-200 bg-white px-3 py-2">
                                          <div className="text-xs text-zinc-500">Votes</div>
                                          <div className="mt-1 break-words text-sm font-medium text-zinc-900">
                                            {Array.isArray(sample.votes) && sample.votes.length
                                              ? sample.votes.join(", ")
                                              : "—"}
                                          </div>
                                        </div>
                                        <div className="rounded-md border border-zinc-200 bg-white px-3 py-2">
                                          <div className="text-xs text-zinc-500">LLM tiebreak</div>
                                          <div className="mt-1 text-sm font-medium text-zinc-900">
                                            {sample.llm_tiebreak ? "enabled" : "disabled"}
                                          </div>
                                        </div>
                                      </div>

                                      {!memberResponses.length ? (
                                        <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-3 text-sm text-amber-800">
                                          Member-level answers are not available for this run.
                                          This result only contains call traces, not per-model raw
                                          answers. It was likely produced before the ensemble
                                          observability update or by an older backend process.
                                          Restart the backend and rerun the experiment to capture
                                          per-model answers here.
                                        </div>
                                      ) : (
                                        <div className="space-y-2">
                                          {memberResponses.map((member) => (
                                            <div
                                              key={`${sample.query_id}-${member.member_index ?? member.model_id}`}
                                              className="rounded-md border border-zinc-200 bg-white px-3 py-3"
                                            >
                                              <div className="flex flex-wrap items-center gap-2">
                                                <Badge variant="secondary">
                                                  Member {member.member_index ?? "?"}
                                                </Badge>
                                                {member.role && (
                                                  <Badge variant="outline">{String(member.role)}</Badge>
                                                )}
                                                <span className="font-mono text-xs text-zinc-500">
                                                  {member.model_id ?? "—"}
                                                </span>
                                              </div>
                                              <div className="mt-2 grid grid-cols-2 gap-2 md:grid-cols-4">
                                                <div className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2">
                                                  <div className="text-xs text-zinc-500">Parsed</div>
                                                  <div className="mt-1 text-sm font-medium text-zinc-900">
                                                    {typeof member.parsed_answer === "string"
                                                      ? member.parsed_answer
                                                      : "—"}
                                                  </div>
                                                </div>
                                                <div className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2">
                                                  <div className="text-xs text-zinc-500">Confidence</div>
                                                  <div className="mt-1 text-sm font-medium text-zinc-900">
                                                    {typeof member.confidence === "number"
                                                      ? formatPercent(member.confidence)
                                                      : "—"}
                                                  </div>
                                                </div>
                                                <div className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2">
                                                  <div className="text-xs text-zinc-500">Latency</div>
                                                  <div className="mt-1 text-sm font-medium text-zinc-900">
                                                    {typeof member.latency_ms === "number"
                                                      ? formatDurationMs(member.latency_ms)
                                                      : "—"}
                                                  </div>
                                                </div>
                                                <div className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2">
                                                  <div className="text-xs text-zinc-500">Tokens</div>
                                                  <div className="mt-1 text-sm font-medium text-zinc-900">
                                                    {typeof member.input_tokens === "number" ||
                                                    typeof member.output_tokens === "number"
                                                      ? `${formatNumber(Number(member.input_tokens ?? 0))} / ${formatNumber(Number(member.output_tokens ?? 0))}`
                                                      : "—"}
                                                  </div>
                                                </div>
                                              </div>
                                              <div className="mt-2">
                                                <div className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">
                                                  Member answer
                                                </div>
                                                <div className="mt-1 whitespace-pre-wrap break-words text-sm leading-5 text-zinc-700">
                                                  {typeof member.raw_text === "string" && member.raw_text.trim()
                                                    ? member.raw_text
                                                    : "Not available"}
                                                </div>
                                              </div>
                                            </div>
                                          ))}
                                        </div>
                                      )}

                                      {sample.llm_tiebreak && (
                                        <div className="rounded-md border border-zinc-200 bg-white px-3 py-3">
                                          <div className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">
                                            LLM tiebreak answer
                                          </div>
                                          <div className="mt-2 whitespace-pre-wrap break-words text-sm leading-5 text-zinc-700">
                                            {typeof sample.llm_tiebreak_raw_text === "string" &&
                                            sample.llm_tiebreak_raw_text.trim()
                                              ? sample.llm_tiebreak_raw_text
                                              : "Not available"}
                                          </div>
                                          <div className="mt-2 text-xs text-zinc-500">
                                            Parsed:{" "}
                                            {typeof sample.llm_tiebreak_parsed_answer === "string"
                                              ? sample.llm_tiebreak_parsed_answer
                                              : "—"}
                                          </div>
                                        </div>
                                      )}
                                    </section>
                                  )}

                                  <section className="space-y-3">
                                    <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                      Core texts
                                    </p>
                                    <div className="space-y-2">
                                      {CORE_TEXT_FIELDS.map((field) => (
                                        <div
                                          key={field}
                                          className="rounded-md border border-zinc-200 bg-white px-3 py-2"
                                        >
                                          <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-zinc-500">
                                            {formatFieldLabel(field)}
                                          </p>
                                          <div className="truncate text-xs text-zinc-700">
                                            {getSampleTextValue(sample, field)}
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </section>

                                  <section className="space-y-3">
                                    <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                      Sample details
                                    </p>
                                    {!detailEntries.length ? (
                                      <p className="text-sm text-zinc-500">
                                        No scalar sample fields available.
                                      </p>
                                    ) : (
                                      <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                                        {detailEntries.map(([key, value]) => (
                                          <div
                                            key={key}
                                            className="rounded-md border border-zinc-200 bg-white px-3 py-2"
                                          >
                                            <div className="text-xs text-zinc-500">
                                              {formatFieldLabel(key)}
                                            </div>
                                            <div className="mt-1 break-words text-sm font-medium text-zinc-900">
                                              {formatScalarValue(value, key)}
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    )}
                                    {sample.resource_estimate && (
                                      <div>
                                        <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                          {formatFieldLabel("resource_estimate")}
                                        </p>
                                        <pre className="whitespace-pre-wrap break-all rounded-md bg-white p-3 text-xs text-zinc-700">
                                          {stringifyJson(sample.resource_estimate)}
                                        </pre>
                                      </div>
                                    )}
                                  </section>

                                  <section className="space-y-3">
                                    <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                      Inference steps
                                    </p>
                                    {(sample.inference_steps?.length ?? 0) === 0 ? (
                                      <p className="text-sm text-zinc-500">
                                        No inference step trace available for this sample.
                                      </p>
                                    ) : (
                                      <div className="space-y-3">
                                        {(sample.inference_steps ?? []).map((step, idx) => (
                                          <div
                                            key={idx}
                                            className="rounded-md border border-zinc-200 bg-white p-3"
                                          >
                                            <div className="mb-3 flex flex-wrap items-center gap-2">
                                              <Badge variant="secondary">Step {idx + 1}</Badge>
                                              {step.role && (
                                                <Badge variant="outline">
                                                  {String(step.role)}
                                                </Badge>
                                              )}
                                              {step.model_id && (
                                                <span className="font-mono text-xs text-zinc-500">
                                                  {String(step.model_id)}
                                                </span>
                                              )}
                                            </div>
                                            <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                                              {getStepEntries(step).map(([key, value]) => (
                                                <div
                                                  key={key}
                                                  className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2"
                                                >
                                                  <div className="text-xs text-zinc-500">
                                                    {formatFieldLabel(key)}
                                                  </div>
                                                  {isScalarValue(value) ? (
                                                    <div className="mt-1 break-words text-sm font-medium text-zinc-900">
                                                      {formatScalarValue(value, key)}
                                                    </div>
                                                  ) : (
                                                    <pre className="mt-1 whitespace-pre-wrap break-all text-xs text-zinc-700">
                                                      {stringifyJson(value)}
                                                    </pre>
                                                  )}
                                                </div>
                                              ))}
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    )}
                                  </section>

                                  <section className="space-y-3">
                                    <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                      Raw JSON
                                    </p>
                                    <pre className="whitespace-pre-wrap break-all rounded-md bg-white p-3 text-xs text-zinc-700">
                                      {stringifyJson(sample)}
                                    </pre>
                                  </section>
                            </div>
                          </div>
                        )}
                      </div>
                    </Fragment>
                  );
                })}
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
                        Models: {Array.from(new Set(steps.map((s) => s.model))).join(", ")}
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
