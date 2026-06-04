"use client";

import Link from "next/link";
import { Fragment, useState, type ReactNode } from "react";
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
  Architecture,
  EnsembleMemberResponse,
  ResultSample,
  ResultSampleInferenceStep,
} from "@/types";

type Tab = "overview" | "metrics" | "samples" | "inference" | "config";
type DetailArchitecture = Architecture | "unknown";
type ScalarValue = string | number | boolean | null | undefined;
type DetailEntry = [string, ScalarValue];
type SummaryCard = {
  label: string;
  value: ReactNode;
};
type DisplayField = {
  key: string;
  value: string;
};
type DisplayRow = {
  label: string;
  value: ReactNode;
};

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "metrics", label: "Metrics" },
  { id: "samples", label: "Samples" },
  { id: "inference", label: "Inference steps" },
  { id: "config", label: "Config" },
];

const KNOWN_ARCHITECTURES: Architecture[] = [
  "monolithic",
  "routing",
  "multi_agent",
  "active_oracle",
  "ensemble",
  "speculative",
  "blackboard",
  "entropy_blackboard",
  "pure_swarm",
];

function isKnownArchitecture(value: string): value is Architecture {
  return KNOWN_ARCHITECTURES.includes(value as Architecture);
}

function toDetailArchitecture(value: string): DetailArchitecture {
  return isKnownArchitecture(value) ? value : "unknown";
}

function formatArchitectureName(value: string): string {
  return value.replace(/_/g, " ");
}

function valueOrDash(value: number | string | null | undefined): string {
  if (value == null) return "—";
  if (typeof value === "number") return formatDecimal(value);
  return value;
}

function formatTokenBudget(value: number | null | undefined): string {
  if (value == null || value <= 0) return "auto";
  return formatNumber(value);
}

function formatCompletedValue(
  createdAt: string | undefined,
  completedAt: string,
): string {
  const completedLabel = formatDate(completedAt);
  if (!createdAt) return completedLabel;

  const createdLabel = formatDate(createdAt);
  const deltaMs = new Date(completedAt).getTime() - new Date(createdAt).getTime();
  if (createdLabel === completedLabel && deltaMs > 0) {
    return `${completedLabel} (+${formatDurationMs(deltaMs)})`;
  }
  return completedLabel;
}

function hasTextValue(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function hasRenderableScalar(value: ScalarValue): boolean {
  if (value == null) return false;
  if (typeof value === "string") return value.trim().length > 0;
  if (typeof value === "number") return !Number.isNaN(value);
  return true;
}

function isScalarValue(value: unknown): value is ScalarValue {
  return (
    value == null ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function sampleUsesLlm(sample: ResultSample): boolean {
  return Boolean(sample.used_llm || sample.escalated || (sample.llm_calls ?? 0) > 0);
}

function hasEnsembleTiebreakEvidence(sample: ResultSample): boolean {
  return (
    sample.llm_tiebreak === true ||
    sampleUsesLlm(sample) ||
    hasTextValue(sample.llm_tiebreak_raw_text) ||
    hasTextValue(sample.llm_tiebreak_parsed_answer)
  );
}

function shouldShowEnsembleTiebreak(
  config: Record<string, unknown>,
  llm: string | null,
  samples: ResultSample[],
): boolean {
  const enabledInConfig = config.llm_tiebreak === true;
  const hasSampleEvidence = samples.some(hasEnsembleTiebreakEvidence);
  return enabledInConfig || (hasTextValue(llm) && hasSampleEvidence);
}

function isArchitectureWithDirectLlm(architecture: DetailArchitecture): boolean {
  return (
    architecture === "monolithic" ||
    architecture === "routing" ||
    architecture === "multi_agent" ||
    architecture === "active_oracle" ||
    architecture === "speculative"
  );
}

function formatFieldLabel(key: string): string {
  const labels: Record<string, string> = {
    prompt_text: "Prompt",
    slm_text: "SLM answer",
    slm_raw_text: "SLM raw answer",
    llm_raw_text: "LLM raw answer",
    final_text: "Final answer",
    final_raw_text: "Final raw answer",
    predicted: "Predicted",
    ground_truth: "Ground truth",
    voting_method: "Voting method",
    vote_counts: "Vote counts",
    votes: "Votes",
    llm_tiebreak: "LLM tiebreak",
    llm_calls: "LLM calls",
    oracle_calls_made: "Oracle calls",
    used_llm: "Used LLM",
    escalated: "Escalated",
    confidence: "Confidence",
    final_model_id: "Final model",
    final_answer_source: "Decision source",
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
    escalation_reason: "Escalation reason",
    resource_estimate: "Resource estimate",
    inference_steps: "Inference steps",
    model_id: "Model",
    host_label: "Host",
    duration_s: "Duration",
    input_tokens: "Input tokens",
    output_tokens: "Output tokens",
    role: "Role",
    accepted_by: "Accepted by",
    confidence_method: "Confidence method",
    parse_success: "Parse success",
    top2_margin: "Top-2 margin",
    input_too_long: "Input too long",
    low_confidence: "Low confidence",
    low_margin: "Low margin",
    forced_escalation: "Forced escalation",
    interrupted: "Interrupted",
    slm_tokens_before_interrupt: "SLM tokens (pre-interrupt)",
    investigation_trace: "Investigation trace",
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

function formatDecisionSource(value: unknown): string | null {
  if (!hasTextValue(value)) return null;
  const normalized = value.trim().toLowerCase();
  if (normalized === "ensemble_vote") return "Ensemble vote";
  if (normalized === "llm_tiebreak") return "LLM tiebreak";
  if (normalized === "slm") return "SLM";
  if (normalized === "llm") return "LLM";
  if (normalized === "none") return "No final answer";
  return value;
}

function stringifyJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

function collectScalarEntries(sample: ResultSample, keys: string[]): DetailEntry[] {
  const entries: DetailEntry[] = [];
  for (const key of keys) {
    const value = sample[key];
    if (isScalarValue(value) && hasRenderableScalar(value)) {
      entries.push([key, value]);
    }
  }
  return entries;
}

function getSampleQuestionPreview(sample: ResultSample): string {
  const promptText = hasTextValue(sample.prompt_text) ? sample.prompt_text.trim() : "";
  if (promptText) return promptText;

  const queryText = hasTextValue(sample.query_text) ? sample.query_text.trim() : "";
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

function getStepEntries(step: ResultSampleInferenceStep): Array<[string, unknown]> {
  return Object.entries(step).sort(([a], [b]) => a.localeCompare(b));
}

function getEnsembleMemberResponses(sample: ResultSample): EnsembleMemberResponse[] {
  return Array.isArray(sample.ensemble_member_responses)
    ? sample.ensemble_member_responses
    : [];
}

function getSampleTextValue(sample: ResultSample, key: string): string | null {
  const value = sample[key];
  return hasTextValue(value) ? value.trim() : null;
}

function getCoreTextFields(
  architecture: DetailArchitecture,
  sample: ResultSample,
): DisplayField[] {
  const keysByArchitecture: Record<DetailArchitecture, string[]> = {
    ensemble: ["prompt_text", "final_text", "predicted", "ground_truth"],
    monolithic: ["prompt_text", "final_text", "predicted", "ground_truth"],
    routing: [
      "prompt_text",
      "slm_text",
      "llm_raw_text",
      "final_text",
      "predicted",
      "ground_truth",
    ],
    multi_agent: [
      "prompt_text",
      "slm_text",
      "llm_raw_text",
      "final_text",
      "predicted",
      "ground_truth",
    ],
    active_oracle: ["prompt_text", "investigation_trace", "slm_raw_text", "predicted", "ground_truth"],
    speculative: [
      "prompt_text",
      "slm_text",
      "llm_raw_text",
      "final_text",
      "predicted",
      "ground_truth",
    ],
    blackboard: ["prompt_text", "final_text", "predicted", "ground_truth"],
    entropy_blackboard: ["prompt_text", "final_text", "predicted", "ground_truth"],
    pure_swarm: ["prompt_text", "final_text", "predicted", "ground_truth"],
    unknown: ["prompt_text", "slm_text", "final_text", "predicted", "ground_truth"],
  };

  return keysByArchitecture[architecture]
    .map((key) => {
      const value = getSampleTextValue(sample, key);
      return value ? { key, value } : null;
    })
    .filter((field): field is DisplayField => field !== null);
}

function getSampleSummaryCards(
  architecture: DetailArchitecture,
  sample: ResultSample,
): SummaryCard[] {
  const cards: SummaryCard[] = [
    {
      label: "Correct",
      value: (
        <Badge variant={sample.correct ? "success" : "destructive"}>
          {sample.correct ? "correct" : "wrong"}
        </Badge>
      ),
    },
  ];

  if (architecture === "routing") {
    cards.push({
      label: "Escalated",
      value: (
        <Badge variant={sampleUsesLlm(sample) ? "warning" : "secondary"}>
          {sampleUsesLlm(sample) ? "yes" : "no"}
        </Badge>
      ),
    });
    if (typeof sample.slm_confidence === "number") {
      cards.push({
        label: "SLM conf.",
        value: formatPercent(sample.slm_confidence),
      });
    }
  } else if (architecture === "ensemble") {
    if (hasRenderableScalar(sample.ground_truth)) {
      cards.push({
        label: "Correct answer",
        value: String(sample.ground_truth),
      });
    }
    const winningVote =
      (hasTextValue(sample.predicted) && sample.predicted) ||
      (Array.isArray(sample.votes) && sample.votes.length > 0 ? sample.votes[0] : null);
    if (hasRenderableScalar(winningVote)) {
      cards.push({
        label: "Winning vote",
        value: String(winningVote),
      });
    }
    const decisionSource = formatDecisionSource(sample.final_answer_source);
    if (decisionSource) {
      cards.push({ label: "Decision", value: decisionSource });
    }
    if (sample.llm_tiebreak === true || hasEnsembleTiebreakEvidence(sample)) {
      cards.push({
        label: "Tiebreak",
        value: (
          <Badge variant={sampleUsesLlm(sample) ? "warning" : "secondary"}>
            {sampleUsesLlm(sample) ? "used" : "enabled"}
          </Badge>
        ),
      });
    }
    if (typeof sample.confidence === "number") {
      cards.push({
        label: "Confidence",
        value: formatPercent(sample.confidence),
      });
    }
  } else if (architecture === "active_oracle") {
    if (typeof sample.oracle_calls_made === "number") {
      cards.push({
        label: "Oracle calls",
        value: formatNumber(sample.oracle_calls_made),
      });
    }
    if (typeof sample.confidence === "number") {
      cards.push({
        label: "Confidence",
        value: formatPercent(sample.confidence),
      });
    }
  } else if (typeof sample.confidence === "number") {
    cards.push({
      label: "Confidence",
      value: formatPercent(sample.confidence),
    });
  }

  if (hasRenderableScalar(sample.final_model_id)) {
    cards.push({
      label: "Final model",
      value: valueOrDash(sample.final_model_id as string | null | undefined),
    });
  }
  if (typeof sample.latency_ms === "number") {
    cards.push({
      label: "Latency",
      value: formatDurationMs(sample.latency_ms),
    });
  }
  if (typeof sample.cost_usd === "number") {
    cards.push({
      label: "Cost",
      value: formatCost(sample.cost_usd),
    });
  }

  return cards;
}

function getArchitectureDetailEntries(
  architecture: DetailArchitecture,
  sample: ResultSample,
): DetailEntry[] {
  if (architecture === "ensemble") {
    return collectScalarEntries(sample, [
      "final_answer_source",
      "final_model_id",
      "confidence",
      "latency_ms",
      "cost_usd",
      "api_cost_usd",
      "infra_cost_usd",
      "energy_kwh",
      "co2_g",
      "gpu_power_w",
    ]);
  }

  if (architecture === "routing") {
    return collectScalarEntries(sample, [
      "final_answer_source",
      "final_model_id",
      "confidence",
      "slm_confidence",
      "confidence_threshold",
      "escalated",
      "llm_calls",
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
      "escalation_reason",
    ]);
  }

  if (architecture === "monolithic") {
    return collectScalarEntries(sample, [
      "final_model_id",
      "confidence",
      "latency_ms",
      "cost_usd",
      "api_cost_usd",
      "infra_cost_usd",
      "energy_kwh",
      "co2_g",
      "gpu_power_w",
    ]);
  }

  const hybridEntries = collectScalarEntries(sample, [
    "final_answer_source",
    "final_model_id",
    "confidence",
    "llm_calls",
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
  ]);

  if (architecture === "multi_agent" || architecture === "speculative") {
    return hybridEntries;
  }

  if (architecture === "active_oracle") {
    const entries = [...hybridEntries];
    entries.push(...collectScalarEntries(sample, ["oracle_calls_made"]));
    return entries;
  }

  if (architecture === "blackboard" || architecture === "entropy_blackboard") {
    return collectScalarEntries(sample, [
      "final_model_id",
      "confidence",
      "llm_calls",
      "latency_ms",
      "cost_usd",
      "api_cost_usd",
      "infra_cost_usd",
      "energy_kwh",
      "co2_g",
      "gpu_power_w",
    ]);
  }

  if (architecture === "pure_swarm") {
    return collectScalarEntries(sample, [
      "final_model_id",
      "confidence",
      "latency_ms",
      "cost_usd",
      "api_cost_usd",
      "infra_cost_usd",
      "energy_kwh",
      "co2_g",
      "gpu_power_w",
    ]);
  }

  return collectScalarEntries(sample, [
    "final_answer_source",
    "final_model_id",
    "confidence",
    "latency_ms",
    "cost_usd",
    "api_cost_usd",
    "infra_cost_usd",
    "energy_kwh",
    "co2_g",
    "gpu_power_w",
  ]);
}

function getRoutingDecisionData(
  sample: ResultSample,
): { decisionEntries: DetailEntry[]; signalEntries: DetailEntry[] } | null {
  if (!isRecord(sample.routing_decision)) return null;

  const decisionEntries: DetailEntry[] = [];
  const signalEntries: DetailEntry[] = [];
  for (const key of ["accepted_by", "threshold", "confidence_method"]) {
    const value = sample.routing_decision[key];
    if (isScalarValue(value) && hasRenderableScalar(value)) {
      decisionEntries.push([key, value]);
    }
  }

  const signals = sample.routing_decision.signals;
  if (isRecord(signals)) {
    for (const [key, value] of Object.entries(signals)) {
      if (isScalarValue(value) && hasRenderableScalar(value)) {
        signalEntries.push([key, value]);
      }
    }
  }

  if (!decisionEntries.length && !signalEntries.length) return null;
  return { decisionEntries, signalEntries };
}

function getOverviewRows({
  architecture,
  benchmark,
  slm,
  llm,
  ensembleSlms,
  config,
  metrics,
  experiment,
  resultDetailCreatedAt,
  showEnsembleTiebreak,
}: {
  architecture: DetailArchitecture;
  benchmark: string;
  slm: string | null;
  llm: string | null;
  ensembleSlms: string[];
  config: Record<string, unknown>;
  metrics: Record<string, number> | null;
  experiment: {
    n_samples?: number;
    created_at?: string;
    completed_at?: string | null;
  } | null;
  resultDetailCreatedAt: string | null;
  showEnsembleTiebreak: boolean;
}): DisplayRow[] {
  const rows: DisplayRow[] = [
    {
      label: "Architecture",
      value: <span className="capitalize">{formatArchitectureName(architecture)}</span>,
    },
    {
      label: "Benchmark",
      value: <span className="uppercase">{benchmark}</span>,
    },
  ];

  if (architecture === "ensemble") {
    rows.push({
      label: "Ensemble SLMs",
      value: ensembleSlms.length ? ensembleSlms.join(", ") : "—",
    });
    if (showEnsembleTiebreak) {
      rows.push({
        label: "LLM tiebreak",
        value: hasTextValue(llm) ? llm : "configured",
      });
    }
  } else if (architecture === "monolithic") {
    rows.push({
      label: "LLM",
      value: llm ?? "—",
    });
  } else if (architecture === "blackboard" || architecture === "entropy_blackboard") {
    rows.push({
      label: "Primary SLM",
      value: slm ?? "—",
    });
    rows.push({
      label: "Secondary SLM",
      value: (config.secondary_slm as string | undefined) ?? "—",
    });
    rows.push({
      label: "Heavy Sweeper",
      value: llm ?? "—",
    });
  } else if (architecture === "pure_swarm") {
    rows.push({
      label: "Primary SLM",
      value: slm ?? "—",
    });
    rows.push({
      label: "Secondary SLM",
      value: (config.secondary_slm as string | undefined) ?? "—",
    });
  } else {
    rows.push({
      label: "SLM",
      value: slm ?? "—",
    });
    if (isArchitectureWithDirectLlm(architecture)) {
      rows.push({
        label: "LLM",
        value: llm ?? "—",
      });
    }
  }

  rows.push({
    label: "Samples",
    value: experiment?.n_samples ?? valueOrDash(metrics?.n_total),
  });

  if (architecture === "routing") {
    rows.push({
      label: "Threshold",
      value: formatPercent(Number(config.confidence_threshold ?? 0.7)),
    });
  }

  if (architecture !== "monolithic") {
    rows.push({
      label: "SLM temp / max tokens",
      value: `${formatDecimal(Number(config.slm_temperature ?? 0))} / ${formatTokenBudget(
        Number(config.slm_max_tokens ?? 0),
      )}`,
    });
  }

  if (
    isArchitectureWithDirectLlm(architecture) ||
    (architecture === "ensemble" && showEnsembleTiebreak)
  ) {
    rows.push({
      label: "LLM temp / max tokens",
      value: `${formatDecimal(Number(config.llm_temperature ?? 0))} / ${formatTokenBudget(
        Number(config.llm_max_tokens ?? 0),
      )}`,
    });
  }

  rows.push({
    label: "Created",
    value: formatDate(experiment?.created_at ?? resultDetailCreatedAt ?? ""),
  });

  if (experiment?.completed_at) {
    rows.push({
      label: "Completed",
      value: formatCompletedValue(experiment.created_at, experiment.completed_at),
    });
  }

  return rows;
}

function DetailGrid({ entries }: { entries: DetailEntry[] }) {
  return (
    <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
      {entries.map(([key, value]) => (
        <div key={key} className="rounded-md border border-zinc-200 bg-white px-3 py-2">
          <div className="text-xs text-zinc-500">{formatFieldLabel(key)}</div>
          <div className="mt-1 break-words text-sm font-medium text-zinc-900">
            {key === "final_answer_source"
              ? formatDecisionSource(value) ?? formatScalarValue(value, key)
              : formatScalarValue(value, key)}
          </div>
        </div>
      ))}
    </div>
  );
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

  const architectureId = String(
    experiment?.architecture ?? resultDetail?.architecture ?? "unknown",
  );
  const architecture = toDetailArchitecture(architectureId);
  const architectureLabel = formatArchitectureName(architectureId);
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
  const nEscalated = Math.round(metrics?.n_escalated ?? 0);
  const llmCallRatio = metrics?.llm_call_ratio ?? 0;
  const hasFallbackCalls = llmCallRatio > 0 || nEscalated > 0;
  const showEnsembleTiebreak = shouldShowEnsembleTiebreak(config, llm, samples);

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
    "rewrite_rate",
    "avg_accepted_draft_ratio",
    "avg_draft_completion_tokens",
    "max_draft_completion_tokens",
    "avg_verifier_requests",
    "avg_verifier_completion_tokens",
  ];

  const allMetricKeys = metrics
    ? [
        ...orderedMetricKeys.filter((k) => metrics[k] != null),
        ...Object.keys(metrics).filter((k) => !orderedMetricKeys.includes(k)),
      ]
    : [];

  const overviewRows = getOverviewRows({
    architecture,
    benchmark,
    slm,
    llm,
    ensembleSlms,
    config,
    metrics,
    experiment: experiment
      ? {
          n_samples: experiment.n_samples,
          created_at: experiment.created_at,
          completed_at: experiment.completed_at,
        }
      : null,
    resultDetailCreatedAt: resultDetail?.created_at ?? null,
    showEnsembleTiebreak,
  });

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
    if (architecture === "active_oracle") {
      return (
        <p>
          The SLM <strong>{slm}</strong> reasons step-by-step and queries the oracle{" "}
          <strong>{llm}</strong> when it needs a factual sub-answer.
        </p>
      );
    }
    if (architecture === "ensemble") {
      return (
        <p>
          {ensembleSlms.length} SLMs voted:{" "}
          <strong>{ensembleSlms.length ? ensembleSlms.join(", ") : "configured members"}</strong>
          {showEnsembleTiebreak ? (
            <>
              {" "}
              · tiebreak <strong>{llm ?? "LLM"}</strong> was available only when no majority
              emerged.
            </>
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
    if (architecture === "blackboard") {
      const secondarySlm = config.secondary_slm as string | undefined;
      return (
        <p>
          Bossless swarm: <strong>{slm}</strong> and <strong>{secondarySlm ?? "secondary SLM"}</strong>{" "}
          competed autonomously on the shared board. <strong>{llm}</strong> acted as the heavy
          sweeper — woken only when a task exceeded its TTL.
        </p>
      );
    }
    if (architecture === "entropy_blackboard") {
      const secondarySlm = config.secondary_slm as string | undefined;
      return (
        <p>
          Entropy swarm: <strong>{slm}</strong> and <strong>{secondarySlm ?? "secondary SLM"}</strong>{" "}
          competed via entropy-based bids. <strong>{llm}</strong> acted as the heavy sweeper —
          woken only when a task exceeded its TTL.
        </p>
      );
    }
    if (architecture === "pure_swarm") {
      const secondarySlm = config.secondary_slm as string | undefined;
      return (
        <p>
          Pure swarm: <strong>{slm}</strong> and <strong>{secondarySlm ?? "secondary SLM"}</strong>{" "}
          competed autonomously without any LLM fallback.
        </p>
      );
    }
    return <p>Architecture: {architectureLabel}.</p>;
  }

  const inferenceSteps = samples.flatMap((sample, sampleIdx) =>
    (sample.inference_steps ?? []).map((step, stepIdx) => ({
      sampleIdx,
      stepIdx,
      queryId: sample.query_id,
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
        {experiment?.status === "queued" && experiment.queue_position != null && (
          <Badge variant="secondary">queue #{experiment.queue_position}</Badge>
        )}
        <Badge variant="outline" className="capitalize">
          {architectureLabel}
        </Badge>
        <Badge variant="secondary" className="uppercase">
          {benchmark}
        </Badge>
      </div>

      <div className="flex gap-1 border-b border-zinc-200">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setTab(item.id)}
            className={`px-3 py-2 text-sm font-medium transition ${
              tab === item.id
                ? "border-b-2 border-zinc-900 text-zinc-900"
                : "text-zinc-500 hover:text-zinc-900"
            }`}
          >
            {item.label}
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
                {overviewRows.map((row) => (
                  <p key={row.label}>
                    <span className="text-zinc-500">{row.label}:</span> {row.value}
                  </p>
                ))}
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
                    "baseline_accuracy",
                    "baseline_algorithmic_latency_ms",
                    "baseline_cost_usd",
                    "baseline_energy_kwh",
                    "baseline_eats_score",
                  ]
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
                      No escalation: every sample was answered by the SLM without LLM fallback.
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
            <LiveProgress
              experimentId={experiment.experiment_id}
              enabled={isActive}
              showRoutingLlmRatio={architecture === "routing"}
              status={experiment.status}
              queuePosition={experiment.queue_position}
            />
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
              <div className="space-y-8">
                {[
                  {
                    title: "Core Performance & EATS",
                    keys: ["accuracy", "eats_score", "ece", "accuracy_ci_low_95", "accuracy_ci_high_95", "n_total", "n_correct", "accuracy_slm_handled", "accuracy_llm_handled", "accuracy_majority_vote"]
                  },
                  {
                    title: "Cost Analysis",
                    keys: ["total_cost_usd", "total_api_cost_usd", "total_infra_cost_usd", "cost_per_query_usd", "cost_slm_path_usd", "cost_escalated_path_usd", "cost_slm_path_fraction", "total_slm_api_cost_usd", "total_llm_api_cost_usd"]
                  },
                  {
                    title: "Latency & Throughput",
                    keys: ["avg_latency_ms", "latency_p50_ms", "latency_p95_ms", "avg_algorithmic_latency_ms", "throughput_tokens_per_sec"]
                  },
                  {
                    title: "Energy & CO2",
                    keys: ["total_energy_kwh", "total_co2_g", "avg_energy_per_sample_kwh", "avg_co2_per_sample_g", "joules_per_output_token", "total_tokens"]
                  },
                  {
                    title: "Architecture & Routing",
                    keys: ["llm_call_ratio", "escalation_rate", "n_escalated", "n_slm_only", "n_llm_final", "avg_slm_confidence", "avg_confidence_escalated", "avg_confidence_non_escalated", "llm_tiebreak_rate", "oracle_query_rate"]
                  },
                  {
                    title: "Normalized (vs Baseline)",
                    keys: ["normalized_cost", "normalized_algorithmic_latency", "normalized_energy", "normalized_efficiency_penalty"]
                  },
                  {
                    title: "Monolithic LLM Baseline",
                    keys: ["baseline_accuracy", "baseline_eats_score", "baseline_ece", "baseline_cost_usd", "baseline_algorithmic_latency_ms", "baseline_energy_kwh"]
                  }
                ].map(group => {
                  const groupKeys = group.keys.filter(k => metrics[k] != null);
                  if (groupKeys.length === 0) return null;
                  return (
                    <div key={group.title} className="space-y-3">
                      <h3 className="text-sm font-semibold text-zinc-900 border-b border-zinc-200 pb-1">{group.title}</h3>
                      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                        {groupKeys.map(key => (
                          <div key={key} className="rounded-md border border-zinc-100 bg-white p-3">
                            <div className="text-xs text-zinc-500">{formatMetricLabel(key)}</div>
                            <div className="text-lg font-semibold text-zinc-900">
                              {formatMetricValue(key, metrics[key])}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
                
                {/* Other remaining metrics not explicitly grouped */}
                {(() => {
                  const usedKeys = new Set([
                    "accuracy", "eats_score", "ece", "accuracy_ci_low_95", "accuracy_ci_high_95", "n_total", "n_correct", "accuracy_slm_handled", "accuracy_llm_handled", "accuracy_majority_vote",
                    "total_cost_usd", "total_api_cost_usd", "total_infra_cost_usd", "cost_per_query_usd", "cost_slm_path_usd", "cost_escalated_path_usd", "cost_slm_path_fraction", "total_slm_api_cost_usd", "total_llm_api_cost_usd",
                    "avg_latency_ms", "latency_p50_ms", "latency_p95_ms", "avg_algorithmic_latency_ms", "throughput_tokens_per_sec",
                    "total_energy_kwh", "total_co2_g", "avg_energy_per_sample_kwh", "avg_co2_per_sample_g", "joules_per_output_token", "total_tokens",
                    "llm_call_ratio", "escalation_rate", "n_escalated", "n_slm_only", "n_llm_final", "avg_slm_confidence", "avg_confidence_escalated", "avg_confidence_non_escalated", "llm_tiebreak_rate", "oracle_query_rate",
                    "normalized_cost", "normalized_algorithmic_latency", "normalized_energy", "normalized_efficiency_penalty",
                    "baseline_accuracy", "baseline_eats_score", "baseline_ece", "baseline_cost_usd", "baseline_algorithmic_latency_ms", "baseline_energy_kwh"
                  ]);
                  const otherKeys = allMetricKeys.filter(k => !usedKeys.has(k) && metrics[k] != null);
                  if (otherKeys.length === 0) return null;
                  return (
                    <div className="space-y-3">
                      <h3 className="text-sm font-semibold text-zinc-900 border-b border-zinc-200 pb-1">Other Metrics</h3>
                      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                        {otherKeys.map(key => (
                          <div key={key} className="rounded-md border border-zinc-100 bg-white p-3">
                            <div className="text-xs text-zinc-500">{formatMetricLabel(key)}</div>
                            <div className="text-lg font-semibold text-zinc-900">
                              {formatMetricValue(key, metrics[key])}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()}
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
                  const isExpanded = Boolean(expanded[sample.query_id]);
                  const summaryCards = getSampleSummaryCards(architecture, sample);
                  const detailEntries = getArchitectureDetailEntries(architecture, sample);
                  const textFields = getCoreTextFields(architecture, sample);
                  const memberResponses = getEnsembleMemberResponses(sample);
                  const routingDecision = architecture === "routing"
                    ? getRoutingDecisionData(sample)
                    : null;
                  const hasInferenceTrace = (sample.inference_steps?.length ?? 0) > 0;
                  const hasResourceEstimate = isRecord(sample.resource_estimate);
                  const showEnsembleDecisionSection =
                    architecture === "ensemble" &&
                    (
                      memberResponses.length > 0 ||
                      Array.isArray(sample.votes) ||
                      isRecord(sample.vote_counts) ||
                      hasTextValue(sample.voting_method) ||
                      sample.llm_tiebreak === true ||
                      hasEnsembleTiebreakEvidence(sample)
                    );
                  const ensembleDecisionEntries: DetailEntry[] = [];
                  if (hasTextValue(sample.voting_method)) {
                    ensembleDecisionEntries.push(["voting_method", sample.voting_method]);
                  }
                  if (
                    isRecord(sample.vote_counts) &&
                    Object.keys(sample.vote_counts).length > 0
                  ) {
                    ensembleDecisionEntries.push([
                      "vote_counts",
                      Object.entries(sample.vote_counts)
                        .map(([answer, count]) => `${answer}: ${count}`)
                        .join(" · "),
                    ]);
                  }
                  if (Array.isArray(sample.votes) && sample.votes.length > 0) {
                    ensembleDecisionEntries.push(["votes", sample.votes.join(", ")]);
                  }
                  if (sample.llm_tiebreak === true || hasEnsembleTiebreakEvidence(sample)) {
                    ensembleDecisionEntries.push([
                      "llm_tiebreak",
                      sampleUsesLlm(sample) ? "used" : "enabled",
                    ]);
                  }
                  const showLegacyEnsembleNote =
                    architecture === "ensemble" && memberResponses.length === 0;
                  const showTiebreakAnswer =
                    architecture === "ensemble" &&
                    (sample.llm_tiebreak === true || hasEnsembleTiebreakEvidence(sample)) &&
                    (hasTextValue(sample.llm_tiebreak_raw_text) ||
                      hasTextValue(sample.llm_tiebreak_parsed_answer));

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
                            {summaryCards.map((card) => (
                              <div
                                key={card.label}
                                className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2"
                              >
                                <div className="text-[11px] uppercase tracking-wide text-zinc-500">
                                  {card.label}
                                </div>
                                <div className="mt-1 break-words text-sm font-medium text-zinc-900">
                                  {card.value}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {isExpanded && (
                          <div className="border-t border-zinc-200 bg-zinc-50/70 px-4 py-4">
                            <div className="space-y-4">
                              {showEnsembleDecisionSection && (
                                <section className="space-y-3">
                                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    Ensemble decision
                                  </p>

                                  {ensembleDecisionEntries.length > 0 && (
                                    <DetailGrid entries={ensembleDecisionEntries} />
                                  )}

                                  {showLegacyEnsembleNote && (
                                    <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-3 text-sm text-amber-800">
                                      This legacy ensemble result does not include member-level
                                      observability, so only the available vote outcome is shown.
                                    </div>
                                  )}

                                  {memberResponses.length > 0 && (
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
                                            {hasRenderableScalar(member.parsed_answer) && (
                                              <div className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2">
                                                <div className="text-xs text-zinc-500">Parsed</div>
                                                <div className="mt-1 text-sm font-medium text-zinc-900">
                                                  {String(member.parsed_answer)}
                                                </div>
                                              </div>
                                            )}
                                            {typeof member.confidence === "number" && (
                                              <div className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2">
                                                <div className="text-xs text-zinc-500">Confidence</div>
                                                <div className="mt-1 text-sm font-medium text-zinc-900">
                                                  {formatPercent(member.confidence)}
                                                </div>
                                              </div>
                                            )}
                                            {typeof member.latency_ms === "number" && (
                                              <div className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2">
                                                <div className="text-xs text-zinc-500">Latency</div>
                                                <div className="mt-1 text-sm font-medium text-zinc-900">
                                                  {formatDurationMs(member.latency_ms)}
                                                </div>
                                              </div>
                                            )}
                                            {(typeof member.input_tokens === "number" ||
                                              typeof member.output_tokens === "number") && (
                                              <div className="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2">
                                                <div className="text-xs text-zinc-500">Tokens (in / out)</div>
                                                <div className="mt-1 text-sm font-medium text-zinc-900">
                                                  {`${formatNumber(Number(member.input_tokens ?? 0))} / ${formatNumber(Number(member.output_tokens ?? 0))}`}
                                                </div>
                                                {(typeof member.effective_max_tokens === "number" ||
                                                  hasTextValue(member.finish_reason)) && (
                                                  <div className="mt-1 text-xs text-zinc-500">
                                                    {typeof member.effective_max_tokens === "number"
                                                      ? `max ${formatNumber(Number(member.effective_max_tokens))}`
                                                      : ""}
                                                    {typeof member.effective_max_tokens === "number" &&
                                                    hasTextValue(member.finish_reason)
                                                      ? " · "
                                                      : ""}
                                                    {hasTextValue(member.finish_reason)
                                                      ? member.finish_reason === "length"
                                                        ? "finish: length (truncated)"
                                                        : `finish: ${String(member.finish_reason)}`
                                                      : ""}
                                                  </div>
                                                )}
                                              </div>
                                            )}
                                          </div>
                                          <div className="mt-2">
                                            <div className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">
                                              Member answer
                                            </div>
                                            <div className="mt-1 whitespace-pre-wrap break-words text-sm leading-5 text-zinc-700">
                                              {hasTextValue(member.raw_text)
                                                ? member.raw_text
                                                : "Not available"}
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  )}

                                  {showTiebreakAnswer && (
                                    <div className="rounded-md border border-zinc-200 bg-white px-3 py-3">
                                      <div className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">
                                        LLM tiebreak answer
                                      </div>
                                      {hasTextValue(sample.llm_tiebreak_raw_text) && (
                                        <div className="mt-2 whitespace-pre-wrap break-words text-sm leading-5 text-zinc-700">
                                          {sample.llm_tiebreak_raw_text}
                                        </div>
                                      )}
                                      {hasTextValue(sample.llm_tiebreak_parsed_answer) && (
                                        <div className="mt-2 text-xs text-zinc-500">
                                          Parsed: {sample.llm_tiebreak_parsed_answer}
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </section>
                              )}

                              {routingDecision && (
                                <section className="space-y-3">
                                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    Routing decision
                                  </p>
                                  {routingDecision.decisionEntries.length > 0 && (
                                    <DetailGrid entries={routingDecision.decisionEntries} />
                                  )}
                                  {routingDecision.signalEntries.length > 0 && (
                                    <div className="space-y-2">
                                      <div className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                        Decision signals
                                      </div>
                                      <DetailGrid entries={routingDecision.signalEntries} />
                                    </div>
                                  )}
                                </section>
                              )}

                              {textFields.length > 0 && (
                                <section className="space-y-3">
                                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    Core texts
                                  </p>
                                  <div className="space-y-2">
                                    {textFields.map((field) => (
                                      <div
                                        key={field.key}
                                        className="rounded-md border border-zinc-200 bg-white px-3 py-2"
                                      >
                                        <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-zinc-500">
                                          {formatFieldLabel(field.key)}
                                        </p>
                                        <div className="whitespace-pre-wrap break-words text-sm leading-5 text-zinc-700">
                                          {field.value}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </section>
                              )}

                              {detailEntries.length > 0 && (
                                <section className="space-y-3">
                                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    Sample details
                                  </p>
                                  <DetailGrid entries={detailEntries} />
                                </section>
                              )}

                              {hasResourceEstimate && (
                                <section className="space-y-3">
                                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    {formatFieldLabel("resource_estimate")}
                                  </p>
                                  <pre className="whitespace-pre-wrap break-all rounded-md bg-white p-3 text-xs text-zinc-700">
                                    {stringifyJson(sample.resource_estimate)}
                                  </pre>
                                </section>
                              )}

                              {hasInferenceTrace && (
                                <section className="space-y-3">
                                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                                    Inference steps
                                  </p>
                                  <div className="space-y-3">
                                    {(sample.inference_steps ?? []).map((step, idx) => (
                                      <div
                                        key={idx}
                                        className="rounded-md border border-zinc-200 bg-white p-3"
                                      >
                                        <div className="mb-3 flex flex-wrap items-center gap-2">
                                          <Badge variant="secondary">Step {idx + 1}</Badge>
                                          {step.role && (
                                            <Badge variant="outline">{String(step.role)}</Badge>
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
                                </section>
                              )}

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
                  const totalLat = steps.reduce((sum, entry) => sum + entry.latency, 0);
                  const totalIn = steps.reduce((sum, entry) => sum + entry.tokensIn, 0);
                  const totalOut = steps.reduce((sum, entry) => sum + entry.tokensOut, 0);
                  const totalCost = steps.reduce((sum, entry) => sum + entry.cost, 0);
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
                        Models: {Array.from(new Set(steps.map((step) => step.model))).join(", ")}
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
