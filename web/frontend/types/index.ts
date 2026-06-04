export type Architecture =
  | "monolithic"
  | "routing"
  | "multi_agent"
  | "active_oracle"
  | "ensemble"
  | "speculative"
  | "blackboard"
  | "entropy_blackboard"
  | "pure_swarm"
  | "dynamic_bidding";

export type ArchitectureMode = "monolithic" | "hybrid" | "ensemble" | "swarm";

export type Benchmark =
  | "mmlu"
  | "arc"
  | "hellaswag"
  | "gsm8k"
  | "truthfulqa"
  | "humaneval_plus"
  | "livecodebench"
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
  slm?: string | null;
  secondary_slm?: string | null;
  llm?: string | null;
  ensemble_slms?: string[];
  config_overrides?: Record<string, unknown>;
}

export interface ExperimentResponse {
  experiment_id: string;
  status: ExperimentStatus;
  architecture: Architecture;
  benchmark: Benchmark;
  n_samples: number;
  slm: string | null;
  secondary_slm: string | null;
  llm: string | null;
  ensemble_slms: string[];
  config_overrides: Record<string, unknown>;
  created_at: string;
  completed_at: string | null;
  metrics: Record<string, number> | null;
  progress: number;
  total: number;
  error: string | null;
  queue_position: number | null;
}

export interface ExperimentLaunchResponse {
  experiment_id: string;
  status: ExperimentStatus;
  queue_position?: number | null;
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
  host_id?: string | null;
  host_label?: string | null;
  is_active_on_host?: boolean | null;
  shared_host: boolean;
}

export interface ModelListResponse {
  slm: ModelInfo[];
  llm: ModelInfo[];
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
  slm: string | null;
  llm: string | null;
  ensemble_slms: string[];
  accuracy: number;
  avg_latency_ms: number | null;
  avg_algorithmic_latency_ms: number | null;
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

export interface ResultSampleInferenceStep {
  role?: string;
  model_id?: string;
  latency_ms?: number;
  input_tokens?: number;
  output_tokens?: number;
  api_cost_usd?: number;
  [key: string]: unknown;
}

export interface EnsembleMemberResponse {
  member_index?: number;
  role?: string;
  model_id?: string;
  raw_text?: string | null;
  parsed_answer?: string | null;
  parse_status?: string | null;
  confidence?: number | null;
  input_tokens?: number | null;
  output_tokens?: number | null;
  effective_max_tokens?: number | null;
  finish_reason?: string | null;
  latency_ms?: number | null;
  cost_usd?: number | null;
  [key: string]: unknown;
}

export interface ResultSample {
  query_id: string;
  query_text?: string;
  query_choices?: string[] | null;
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
  inference_steps?: ResultSampleInferenceStep[];
  ensemble_member_responses?: EnsembleMemberResponse[];
  vote_counts?: Record<string, number>;
  votes?: string[];
  voting_method?: string;
  llm_tiebreak?: boolean;
  llm_tiebreak_raw_text?: string | null;
  llm_tiebreak_parsed_answer?: string | null;
  oracle_calls_made?: number | null;
  interrupted?: boolean | null;
  slm_tokens_before_interrupt?: number | null;
  prompt_text?: string | null;
  slm_text?: string | null;
  final_text?: string | null;
  [key: string]: unknown;
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
  type: "progress" | "metric" | "complete" | "error" | "status";
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

// --- New: architecture catalog ---
export interface ArchitectureParamSpec {
  key: string;
  label: string;
  type: "float" | "int" | "bool" | "enum" | "string";
  default: unknown;
  min?: number | null;
  max?: number | null;
  options?: string[] | null;
  description?: string | null;
}

export interface ArchitectureSpec {
  id: Architecture;
  name: string;
  mode: ArchitectureMode;
  description: string;
  requires_slm: boolean;
  requires_llm: boolean;
  supports_multi_slm: boolean;
  requires_secondary_slm?: boolean;
  experimental: boolean;
  params: ArchitectureParamSpec[];
}

// --- New: hosts ---
export interface HostStatus {
  host_id: string;
  label: string;
  base_url?: string | null;
  shared: boolean;
  configured_models: string[];
  active_model_id?: string | null;
  active_served_ids: string[];
  is_reachable: boolean;
  locked: boolean;
  lock_holder?: string | null;
  last_probe_latency_ms?: number | null;
  notes?: string | null;
}

export interface HostsResponse {
  hosts: HostStatus[];
  autoswitch_enabled: boolean;
}

// --- New: playground ---
export interface PlaygroundChatRequest {
  model_id: string;
  prompt: string;
  system?: string | null;
  temperature?: number;
  max_tokens?: number;
}

export interface PlaygroundChatResponse {
  model_id: string;
  text: string;
  latency_ms: number;
  model_latency_ms?: number | null;
  completed_at?: string | null;
  input_tokens: number;
  output_tokens: number;
  effective_max_tokens?: number;
  cost_usd: number;
  energy_kwh?: number | null;
  co2_g?: number | null;
  gpu_power_w?: number | null;
  infra_cost_usd?: number | null;
  base_url?: string | null;
  finish_reason?: string | null;
}
