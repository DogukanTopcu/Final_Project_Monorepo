"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useInstances() {
  return useQuery({
    queryKey: ["instances"],
    queryFn: api.listInstances,
    refetchInterval: 15000,
  });
}

export function useCosts() {
  return useQuery({
    queryKey: ["costs"],
    queryFn: api.getCosts,
    refetchInterval: 60000,
  });
}

export function useStartInstance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.startInstance(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["instances"] });
    },
  });
}

export function useStopInstance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.stopInstance(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["instances"] });
    },
  });
}
