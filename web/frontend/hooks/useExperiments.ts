"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ExperimentCreate, ResultDetail } from "@/types";

export function useExperiments() {
  return useQuery({
    queryKey: ["experiments"],
    queryFn: api.listExperiments,
    refetchInterval: 5000,
  });
}

export function useExperiment(id: string) {
  return useQuery({
    queryKey: ["experiments", id],
    queryFn: () => api.getExperiment(id),
    refetchInterval: 3000,
  });
}

export function useLaunchExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ExperimentCreate) => api.launchExperiment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["experiments"] });
    },
  });
}

export function useCancelExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.cancelExperiment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["experiments"] });
    },
  });
}

export function useResults() {
  return useQuery({
    queryKey: ["results"],
    queryFn: api.listResults,
  });
}

interface UseResultOptions {
  expectedSamples?: number | null;
}

export function useResult(id: string, options?: UseResultOptions) {
  return useQuery<ResultDetail | null>({
    queryKey: ["results", id],
    queryFn: async () => {
      try {
        return await api.getResult(id);
      } catch (error) {
        if (error instanceof Error && error.message.startsWith("API 404:")) {
          return null;
        }
        throw error;
      }
    },
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return 3000;
      if ((options?.expectedSamples ?? 0) > 0 && data.samples.length === 0) {
        return 3000;
      }
      return false;
    },
  });
}

export function useCompareResults(ids: string[]) {
  return useQuery({
    queryKey: ["results", "compare", ids],
    queryFn: () => api.compareResults(ids),
    enabled: ids.length >= 2,
  });
}

export function useModels() {
  return useQuery({
    queryKey: ["models"],
    queryFn: api.listModels,
  });
}

export function useBenchmarks() {
  return useQuery({
    queryKey: ["benchmarks"],
    queryFn: api.listBenchmarks,
  });
}

export function useArchitectures() {
  return useQuery({
    queryKey: ["architectures"],
    queryFn: api.listArchitectures,
  });
}

export function useHosts() {
  return useQuery({
    queryKey: ["hosts"],
    queryFn: api.listHosts,
    refetchInterval: 10000,
  });
}
