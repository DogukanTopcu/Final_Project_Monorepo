import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString();
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatCost(value: number): string {
  return `$${value.toFixed(2)}`;
}

export function formatDurationMs(value: number): string {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(2)}s`;
  }
  return `${value.toFixed(1)}ms`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat().format(value);
}

export function formatDecimal(value: number, digits = 2): string {
  return value.toFixed(digits);
}

export function formatMetricLabel(key: string): string {
  const labels: Record<string, string> = {
    accuracy: "Accuracy",
    llm_call_ratio: "LLM Call Ratio",
    avg_latency_ms: "Average Latency",
    total_cost_usd: "Total Cost",
    n_total: "Total Samples",
    n_correct: "Correct Samples",
    eats_score: "EATS Score",
    normalized_cost: "Normalized Cost",
    latency_p50_ms: "Latency P50",
    latency_p95_ms: "Latency P95",
    total_tokens: "Total Tokens",
    n_escalated: "Escalated Samples",
    escalation_rate: "Escalation Rate",
    n_slm_only: "SLM-only Samples",
    n_llm_final: "LLM Final Answers",
    avg_slm_confidence: "Average SLM Confidence",
    avg_confidence_escalated: "Avg Escalated Confidence",
    avg_confidence_non_escalated: "Avg Non-escalated Confidence",
  };
  return labels[key] ?? key;
}

export function formatMetricValue(key: string, value: number): string {
  if (key.includes("cost")) {
    return formatCost(value);
  }
  if (key.includes("latency")) {
    return formatDurationMs(value);
  }
  if (key.includes("ratio") || key === "accuracy" || key.includes("confidence")) {
    return formatPercent(value);
  }
  if (key === "total_tokens" || key.startsWith("n_")) {
    return formatNumber(Math.round(value));
  }
  return formatDecimal(value);
}
