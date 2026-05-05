"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ExperimentCreate } from "@/types";

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

export function useResult(id: string) {
  return useQuery({
    queryKey: ["results", id],
    queryFn: () => api.getResult(id),
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
