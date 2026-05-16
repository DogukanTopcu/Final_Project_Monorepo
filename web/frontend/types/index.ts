export type Architecture = "routing" | "multi_agent" | "ensemble";
export type Benchmark = "mmlu" | "arc" | "hellaswag" | "gsm8k" | "truthfulqa";
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
  provider: string;
  type: "slm" | "llm";
  status: string;
}

export interface ModelListResponse {
  slm: ModelInfo[];
  llm: ModelInfo[];
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
  eats_score: number | null;
  llm_call_ratio: number | null;
  total_cost: number | null;
  created_at: string;
}

export interface ResultDetail {
  id: string;
  experiment_id: string;
  architecture: string;
  benchmark: string;
  metrics: Record<string, number>;
  samples: Record<string, unknown>[];
  config: Record<string, unknown>;
  created_at: string;
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
  zone: string | null;
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
