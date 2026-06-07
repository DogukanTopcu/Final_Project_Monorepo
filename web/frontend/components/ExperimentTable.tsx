"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { useExperiments } from "@/hooks/useExperiments";
import { formatDate, formatPercent } from "@/lib/utils";
import type { ExperimentResponse, ExperimentStatus } from "@/types";

const statusVariant: Record<ExperimentStatus, "success" | "warning" | "destructive" | "secondary" | "default"> = {
  completed: "success",
  running: "warning",
  queued: "secondary",
  failed: "destructive",
  cancelled: "default",
};

const ALL_FILTER = "all";
const STATUS_ORDER: ExperimentStatus[] = ["running", "queued", "completed", "failed", "cancelled"];

function formatArchitectureLabel(value: string) {
  return value.replace(/_/g, " ");
}

function getExperimentModelsText(exp: ExperimentResponse) {
  if (exp.architecture === "monolithic") {
    return exp.llm ?? "—";
  }

  if (exp.architecture === "multi_agent") {
    const arbitratorRole = exp.config_overrides?.arbitrator === "slm" ? "slm" : "llm";
    if (arbitratorRole === "slm") {
      return `${exp.slm ?? "—"} (all roles)`;
    }
    return `${exp.slm ?? "—"} → arbitrator ${exp.llm ?? "—"}`;
  }

  if (exp.architecture === "ensemble" && exp.ensemble_slms?.length) {
    return `${exp.ensemble_slms.join(", ")}${exp.llm ? ` → tiebreak ${exp.llm}` : ""}`;
  }

  if (exp.architecture === "pure_swarm") {
    return `${exp.slm ?? "—"} / ${exp.secondary_slm ?? "—"}`;
  }

  if (exp.architecture === "blackboard" || exp.architecture === "entropy_blackboard") {
    return `${exp.slm ?? "—"} / ${exp.secondary_slm ?? "—"} / ${exp.llm ?? "—"}`;
  }

  return `${exp.slm ?? "—"} / ${exp.llm ?? "—"}`;
}

function formatStatusLabel(exp: ExperimentResponse) {
  if (exp.status === "queued" && exp.queue_position != null) {
    return `queued · #${exp.queue_position}`;
  }
  return exp.status;
}

export function ExperimentTable() {
  const { data: experiments, isLoading } = useExperiments();
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>(ALL_FILTER);
  const [architectureFilter, setArchitectureFilter] = useState<string>(ALL_FILTER);
  const [benchmarkFilter, setBenchmarkFilter] = useState<string>(ALL_FILTER);

  const statusOptions = useMemo(
    () => [
      ALL_FILTER,
      ...STATUS_ORDER.filter((status) => experiments?.some((exp) => exp.status === status)),
    ],
    [experiments],
  );

  const architectureOptions = useMemo(
    () =>
      [
        ALL_FILTER,
        ...Array.from(new Set((experiments ?? []).map((exp) => exp.architecture))).sort((a, b) =>
          a.localeCompare(b),
        ),
      ] as string[],
    [experiments],
  );

  const benchmarkOptions = useMemo(
    () =>
      [
        ALL_FILTER,
        ...Array.from(new Set((experiments ?? []).map((exp) => exp.benchmark))).sort((a, b) =>
          a.localeCompare(b),
        ),
      ] as string[],
    [experiments],
  );

  const filteredExperiments = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return (experiments ?? []).filter((exp) => {
      if (statusFilter !== ALL_FILTER && exp.status !== statusFilter) {
        return false;
      }

      if (architectureFilter !== ALL_FILTER && exp.architecture !== architectureFilter) {
        return false;
      }

      if (benchmarkFilter !== ALL_FILTER && exp.benchmark !== benchmarkFilter) {
        return false;
      }

      if (!normalizedQuery) {
        return true;
      }

      return [exp.experiment_id, getExperimentModelsText(exp)]
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery);
    });
  }, [architectureFilter, benchmarkFilter, experiments, query, statusFilter]);

  const hasActiveFilters =
    query.trim().length > 0 ||
    statusFilter !== ALL_FILTER ||
    architectureFilter !== ALL_FILTER ||
    benchmarkFilter !== ALL_FILTER;

  function resetFilters() {
    setQuery("");
    setStatusFilter(ALL_FILTER);
    setArchitectureFilter(ALL_FILTER);
    setBenchmarkFilter(ALL_FILTER);
  }

  if (isLoading) {
    return <p className="text-zinc-500">Loading experiments...</p>;
  }

  if (!experiments?.length) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-zinc-500">
          No experiments yet.{" "}
          <Link href="/experiments/new" className="text-zinc-900 underline">
            Launch one
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="gap-4 border-b border-zinc-100">
        <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <CardTitle>Experiments</CardTitle>
            <p className="text-sm text-zinc-500">
              Filter runs by status, architecture, benchmark or model.
            </p>
          </div>
          <div className="text-xs text-zinc-500">
            {filteredExperiments.length} / {experiments.length} shown
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          <div className="flex flex-col gap-1.5 md:col-span-2 xl:col-span-1">
            <label htmlFor="experiment-search" className="text-sm font-medium text-zinc-700">
              Search
            </label>
            <input
              id="experiment-search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Experiment ID or model"
              className="h-10 rounded-md border border-zinc-300 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
            />
          </div>

          <Select
            id="experiment-status-filter"
            label="Status"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            {statusOptions.map((option) => (
              <option key={option} value={option}>
                {option === ALL_FILTER ? "All statuses" : option}
              </option>
            ))}
          </Select>

          <Select
            id="experiment-architecture-filter"
            label="Architecture"
            value={architectureFilter}
            onChange={(event) => setArchitectureFilter(event.target.value)}
          >
            {architectureOptions.map((option) => (
              <option key={option} value={option}>
                {option === ALL_FILTER ? "All architectures" : formatArchitectureLabel(option)}
              </option>
            ))}
          </Select>

          <Select
            id="experiment-benchmark-filter"
            label="Benchmark"
            value={benchmarkFilter}
            onChange={(event) => setBenchmarkFilter(event.target.value)}
          >
            {benchmarkOptions.map((option) => (
              <option key={option} value={option}>
                {option === ALL_FILTER ? "All benchmarks" : option}
              </option>
            ))}
          </Select>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">
            Status: {statusFilter === ALL_FILTER ? "all" : statusFilter}
          </Badge>
          <Badge variant="secondary">
            Architecture:{" "}
            {architectureFilter === ALL_FILTER
              ? "all"
              : formatArchitectureLabel(architectureFilter)}
          </Badge>
          <Badge variant="secondary">
            Benchmark: {benchmarkFilter === ALL_FILTER ? "all" : benchmarkFilter}
          </Badge>
          {query.trim() && <Badge variant="secondary">Search: {query.trim()}</Badge>}
          {hasActiveFilters && (
            <Button type="button" variant="ghost" size="sm" onClick={resetFilters}>
              Clear filters
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        {filteredExperiments.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-zinc-200 text-zinc-500">
                  <th className="pb-3 pr-4 font-medium">ID</th>
                  <th className="pb-3 pr-4 font-medium">Sample Size</th>
                  <th className="pb-3 pr-4 font-medium">Architecture</th>
                  <th className="pb-3 pr-4 font-medium">Benchmark</th>
                  <th className="pb-3 pr-4 font-medium">Models</th>
                  <th className="pb-3 pr-4 font-medium">Status</th>
                  <th className="pb-3 pr-4 font-medium">Accuracy</th>
                  <th className="pb-3 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {filteredExperiments.map((exp) => (
                  <tr
                    key={exp.experiment_id}
                    className="border-b border-zinc-100 hover:bg-zinc-50"
                  >
                    <td className="py-3 pr-4">
                      <Link
                        href={`/experiments/${exp.experiment_id}`}
                        className="font-mono text-zinc-900 underline-offset-2 hover:underline"
                      >
                        {exp.experiment_id}
                      </Link>
                    </td>
                    <td className="py-3 pr-4">{exp.n_samples ?? "—"}</td>
                    <td className="py-3 pr-4 capitalize">
                      {formatArchitectureLabel(exp.architecture)}
                    </td>
                    <td className="py-3 pr-4 uppercase">{exp.benchmark}</td>
                    <td className="py-3 pr-4">{getExperimentModelsText(exp)}</td>
                    <td className="py-3 pr-4">
                      <Badge variant={statusVariant[exp.status]}>{formatStatusLabel(exp)}</Badge>
                    </td>
                    <td className="py-3 pr-4">
                      {exp.metrics?.accuracy != null ? formatPercent(exp.metrics.accuracy) : "—"}
                    </td>
                    <td className="py-3">{formatDate(exp.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-zinc-200 bg-zinc-50 px-4 py-8 text-center">
            <p className="text-sm font-medium text-zinc-900">No experiments match these filters.</p>
            <p className="mt-1 text-sm text-zinc-500">
              Clear the filters to see the full experiment history.
            </p>
            <div className="mt-4">
              <Button type="button" variant="outline" onClick={resetFilters}>
                Reset filters
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
