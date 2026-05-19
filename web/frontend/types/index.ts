export type Architecture = "routing" | "multi_agent" | "ensemble";
export type Benchmark =
  | "mmlu"
  | "arc"
  | "hellaswag"
  | "gsm8k"
  | "truthfulqa"
  | "custom_stratified";
export type ExperimentStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export interface ExperimentCreate {
  architecture: Architecture;
  benchmark: Benchmark;
  n_samples: number;
  slm: string;
  llm: string;
  config_overrides?: Record<string, unknown>;
}

export interface ExperimentResponse {
  experiment_id: string;
  status: ExperimentStatus;
  architecture: Architecture;
  benchmark: Benchmark;
  n_samples: number;
  slm: string;
  llm: string;
  config_overrides: Record<string, unknown>;
  created_at: string;
  completed_at: string | null;
  metrics: Record<string, number> | null;
  progress: number;
  total: number;
  error: string | null;
}

export interface ExperimentLaunchResponse {
  experiment_id: string;
  status: ExperimentStatus;
}

export interface ModelInfo {
  id: string;
  name: string;
  family: string;
  tier: string;
  provider: string;
  runtime_provider: string;
  type: "slm" | "llm";
  configured: boolean;
  status: string;
  base_url?: string | null;
  reason?: string | null;
}

export interface ModelListResponse {
  slm: ModelInfo[];
  llm: ModelInfo[];
  runtime_mode: string;
  force_vllm: boolean;
  warnings: string[];
}

export interface ModelPingResponse {
  model_id: string;
  reachable: boolean;
  latency_ms: number | null;
}

export interface ResultSummary {
  id: string;
  experiment_id: string;
  architecture: string;
  benchmark: string;
  slm: string;
  llm: string;
  accuracy: number;
  avg_latency_ms: number | null;
  eats_score: number | null;
  llm_call_ratio: number | null;
  total_cost_usd: number | null;
  total_energy_kwh: number | null;
  total_infra_cost_usd: number | null;
  created_at: string;
}

export interface ResultDetail {
  id: string;
  experiment_id: string;
  architecture: string;
  benchmark: string;
  metrics: Record<string, number>;
  samples: ResultSample[];
  config: Record<string, unknown>;
  created_at: string;
}

export interface ResultSample {
  query_id: string;
  query_text?: string;
  correct: boolean;
  predicted?: string | null;
  ground_truth?: string | null;
  llm_calls?: number;
  confidence?: number;
  latency_ms?: number;
  cost_usd?: number;
  api_cost_usd?: number;
  infra_cost_usd?: number;
  energy_kwh?: number;
  co2_g?: number;
  gpu_power_w?: number;
  final_model_id?: string | null;
  used_llm?: boolean;
  escalated?: boolean;
  slm_confidence?: number;
  confidence_threshold?: number | null;
  slm_latency_ms?: number | null;
  llm_latency_ms?: number | null;
  slm_input_tokens?: number | null;
  slm_output_tokens?: number | null;
  llm_input_tokens?: number | null;
  llm_output_tokens?: number | null;
  slm_cost_usd?: number | null;
  llm_cost_usd?: number | null;
  resource_estimate?: Record<string, unknown> | null;
  inference_steps?: Record<string, unknown>[];
  prompt_text?: string | null;
  slm_text?: string | null;
  final_text?: string | null;
}

export interface ComparisonResponse {
  ids: string[];
  metrics: Record<string, Record<string, number>>;
}

export interface InstanceInfo {
  instance_id: string;
  name: string;
  instance_type: string;
  state: string;
  public_ip: string | null;
  private_ip: string | null;
  launch_time: string | null;
  tags: Record<string, string>;
}

export interface CostEstimate {
  total_monthly: number;
  breakdown: Record<string, number>;
  currency: string;
}

export interface SSEEvent {
  type: "progress" | "metric" | "complete" | "error";
  completed?: number;
  total?: number;
  current_query?: string;
  name?: string;
  value?: number;
  experiment_id?: string;
  metrics?: Record<string, number>;
  message?: string;
  status?: string;
}

export interface BenchmarkInfo {
  id: string;
  name: string;
  description: string;
  categories: string[];
  total_samples: number;
  suggested_sizes: number[];
}
