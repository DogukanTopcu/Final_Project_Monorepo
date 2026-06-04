"use client";

import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { ArchitectureSummary } from "@/components/analysis/ArchitectureSummary";
import { ParetoScatter } from "@/components/analysis/ParetoScatter";
import { MetricsChart } from "@/components/MetricsChart";
import { useResults } from "@/hooks/useExperiments";
import type { ResultSummary } from "@/types";

const ARCH_OPTIONS = [
  "all",
  "monolithic",
  "routing",
  "multi_agent",
  "active_oracle",
  "ensemble",
  "speculative",
  "blackboard",
  "entropy_blackboard",
  "pure_swarm",
];
const BENCHMARK_OPTIONS = [
  "all",
  "mmlu",
  "arc",
  "hellaswag",
  "gsm8k",
  "truthfulqa",
  "humaneval_plus",
  "livecodebench",
  "custom_stratified",
];

export default function AnalysisPage() {
  const { data: results } = useResults();
  const [archFilter, setArchFilter] = useState("all");
  const [benchmarkFilter, setBenchmarkFilter] = useState("all");
  const [modelFilter, setModelFilter] = useState("");

  const filtered = useMemo(() => {
    let xs: ResultSummary[] = results ?? [];
    if (archFilter !== "all") xs = xs.filter((r) => r.architecture === archFilter);
    if (benchmarkFilter !== "all") xs = xs.filter((r) => r.benchmark === benchmarkFilter);
    if (modelFilter.trim()) {
      const q = modelFilter.trim().toLowerCase();
      xs = xs.filter((r) =>
        [r.slm, r.llm, ...(r.ensemble_slms ?? [])]
          .filter(Boolean)
          .some((m) => String(m).toLowerCase().includes(q)),
      );
    }
    return xs;
  }, [results, archFilter, benchmarkFilter, modelFilter]);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Analysis</h1>
          <p className="text-sm text-zinc-600">
            Aggregated views across every completed run. Filter by architecture, benchmark or
            model and inspect the accuracy/cost/energy tradeoffs.
          </p>
        </div>
        <div className="text-right text-xs text-zinc-500">
          {filtered.length} / {results?.length ?? 0} runs
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <Select
              label="Architecture"
              value={archFilter}
              onChange={(e) => setArchFilter(e.target.value)}
            >
              {ARCH_OPTIONS.map((o) => (
                <option key={o} value={o}>
                  {o === "all" ? "All architectures" : o.replace(/_/g, " ")}
                </option>
              ))}
            </Select>
            <Select
              label="Benchmark"
              value={benchmarkFilter}
              onChange={(e) => setBenchmarkFilter(e.target.value)}
            >
              {BENCHMARK_OPTIONS.map((o) => (
                <option key={o} value={o}>
                  {o === "all" ? "All benchmarks" : o}
                </option>
              ))}
            </Select>
            <div>
              <label className="text-sm font-medium text-zinc-700">Model contains</label>
              <input
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value)}
                placeholder="e.g. qwen, llama"
                className="mt-1 h-10 w-full rounded-md border border-zinc-300 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
              />
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge variant="secondary">
              Arch: {archFilter === "all" ? "all" : archFilter}
            </Badge>
            <Badge variant="secondary">
              Bench: {benchmarkFilter === "all" ? "all" : benchmarkFilter}
            </Badge>
            {modelFilter && <Badge variant="secondary">Model: {modelFilter}</Badge>}
          </div>
        </CardContent>
      </Card>

      <ArchitectureSummary results={filtered} />

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <MetricsChart results={filtered} />
        <ParetoScatter
          title="Accuracy vs cost"
          xKey="total_cost_usd"
          xLabel="Total cost ($)"
          yKey="accuracy"
          yLabel="Accuracy"
          results={filtered}
        />
        <ParetoScatter
          title="Accuracy vs latency"
          xKey="avg_latency_ms"
          xLabel="Avg latency (ms)"
          yKey="accuracy"
          yLabel="Accuracy"
          results={filtered}
        />
        <ParetoScatter
          title="EATS vs total energy"
          xKey="total_energy_kwh"
          xLabel="Total energy (kWh)"
          yKey="eats_score"
          yLabel="EATS"
          results={filtered}
        />
      </div>
    </div>
  );
}
