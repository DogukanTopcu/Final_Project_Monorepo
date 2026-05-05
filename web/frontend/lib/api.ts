import type {
  BenchmarkInfo,
  ComparisonResponse,
  CostEstimate,
  ExperimentCreate,
  ExperimentLaunchResponse,
  ExperimentResponse,
  InstanceInfo,
  ModelListResponse,
  ModelPingResponse,
  ResultDetail,
  ResultSummary,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  listModels: () => request<ModelListResponse>("/api/models"),
  pingModel: (modelId: string) =>
    request<ModelPingResponse>(`/api/models/${modelId}/ping`),

  launchExperiment: (data: ExperimentCreate) =>
    request<ExperimentLaunchResponse>("/api/experiments", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  listExperiments: () => request<ExperimentResponse[]>("/api/experiments"),
  getExperiment: (id: string) =>
    request<ExperimentResponse>(`/api/experiments/${id}`),
  cancelExperiment: (id: string) =>
    request<{ status: string }>(`/api/experiments/${id}`, { method: "DELETE" }),

  listResults: () => request<ResultSummary[]>("/api/results"),
  getResult: (id: string) => request<ResultDetail>(`/api/results/${id}`),
  compareResults: (ids: string[]) =>
    request<ComparisonResponse>(`/api/results/compare?ids=${ids.join(",")}`),

  listInstances: () =>
    request<InstanceInfo[]>("/api/infrastructure/instances"),
  startInstance: (id: string) =>
    request<{ instance_id: string }>(`/api/infrastructure/instances/${id}/start`, {
      method: "POST",
    }),
  stopInstance: (id: string) =>
    request<{ instance_id: string }>(`/api/infrastructure/instances/${id}/stop`, {
      method: "POST",
    }),
  getCosts: () => request<CostEstimate>("/api/infrastructure/costs"),

  listBenchmarks: () => request<BenchmarkInfo[]>("/api/benchmarks"),
};
