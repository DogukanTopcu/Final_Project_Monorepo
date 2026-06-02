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
    avg_algorithmic_latency_ms: "Avg Algorithmic Latency",
    total_cost_usd: "Total Cost",
    n_total: "Total Samples",
    n_correct: "Correct Samples",
    eats_score: "EATS Score",
    normalized_cost: "Normalized Cost",
    normalized_algorithmic_latency: "Normalized Algorithmic Latency",
    latency_p50_ms: "Latency P50",
    latency_p95_ms: "Latency P95",
    total_tokens: "Total Tokens",
    total_energy_kwh: "Total Energy",
    total_co2_g: "Total CO2",
    total_api_cost_usd: "API Cost",
    total_infra_cost_usd: "Infra Cost",
    n_escalated: "Escalated Samples",
    escalation_rate: "Escalation Rate",
    n_slm_only: "SLM-only Samples",
    n_llm_final: "LLM Final Answers",
    avg_slm_confidence: "Average SLM Confidence",
    avg_confidence_escalated: "Avg Escalated Confidence",
    avg_confidence_non_escalated: "Avg Non-escalated Confidence",
    baseline_cost_usd: "Baseline Cost (LLM)",
    baseline_algorithmic_latency_ms: "Baseline Latency (LLM)",
    baseline_energy_kwh: "Baseline Energy (LLM)",
    baseline_accuracy: "Baseline Accuracy (LLM)",
    baseline_eats_score: "Baseline EATS Score (LLM)",
    baseline_ece: "Baseline ECE (LLM)",
    throughput_tokens_per_sec: "Throughput (tokens/sec)",
    cost_per_query_usd: "Cost Per Query",
    joules_per_output_token: "Energy (Joules/token)",
    cost_slm_path_usd: "Cost (SLM path)",
    cost_escalated_path_usd: "Cost (Escalated path)",
    cost_slm_path_fraction: "SLM Path Cost Fraction",
    total_slm_api_cost_usd: "SLM API Cost",
    total_llm_api_cost_usd: "LLM API Cost",
    accuracy_slm_handled: "Accuracy (SLM-handled)",
    accuracy_llm_handled: "Accuracy (LLM-handled)",
    accuracy_majority_vote: "Accuracy (Majority Vote)",
    accuracy_ci_low_95: "Accuracy (95% CI Low)",
    accuracy_ci_high_95: "Accuracy (95% CI High)",
    llm_tiebreak_rate: "LLM Tiebreak Rate",
    oracle_query_rate: "Oracle Query Rate",
    ece: "ECE (Calibration Error)",
    avg_energy_per_sample_kwh: "Avg Energy / Sample",
    avg_co2_per_sample_g: "Avg CO2 / Sample",
    normalized_efficiency_penalty: "Normalized Efficiency Penalty",
  };
  return labels[key] ?? key;
}

export function formatMetricValue(key: string, value: number): string {
  if (key.includes("cost")) {
    return formatCost(value);
  }
  if (key.includes("energy")) {
    return `${value.toFixed(4)} kWh`;
  }
  if (key.includes("co2")) {
    return `${value.toFixed(2)} g`;
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
