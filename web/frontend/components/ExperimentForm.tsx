"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { useLaunchExperiment, useModels, useBenchmarks } from "@/hooks/useExperiments";
import type { Architecture, Benchmark } from "@/types";

export function ExperimentForm() {
  const router = useRouter();
  const { data: models } = useModels();
  const { data: benchmarks } = useBenchmarks();
  const launch = useLaunchExperiment();

  const [architecture, setArchitecture] = useState<Architecture>("routing");
  const [benchmark, setBenchmark] = useState<Benchmark>("mmlu");
  const [nSamples, setNSamples] = useState(100);
  const [slm, setSlm] = useState("qwen3.5-4b");
  const [llm, setLlm] = useState("llama3.3-70b");
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.7);
  const [nModels, setNModels] = useState(3);
  const [dryRun, setDryRun] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const configOverrides: Record<string, unknown> = { dry_run: dryRun };
    if (architecture === "routing") {
      configOverrides.confidence_threshold = confidenceThreshold;
    }
    if (architecture === "ensemble") {
      configOverrides.n_models = nModels;
    }

    const result = await launch.mutateAsync({
      architecture,
      benchmark,
      n_samples: nSamples,
      slm,
      llm,
      config_overrides: configOverrides,
    });
    router.push(`/experiments/${result.experiment_id}`);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Launch Experiment</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <Select
            label="Architecture"
            value={architecture}
            onChange={(e) => setArchitecture(e.target.value as Architecture)}
          >
            <option value="routing">Arch A — Routing</option>
            <option value="multi_agent">Arch B — Multi-Agent</option>
            <option value="ensemble">Arch C — Ensemble</option>
          </Select>

          <Select
            label="Benchmark"
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value as Benchmark)}
          >
            {benchmarks?.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name} — {b.description}
              </option>
            )) ?? (
              <>
                <option value="mmlu">MMLU</option>
                <option value="arc">ARC</option>
                <option value="hellaswag">HellaSwag</option>
                <option value="gsm8k">GSM8K</option>
                <option value="truthfulqa">TruthfulQA</option>
              </>
            )}
          </Select>

          <Select
            label="SLM (Small Language Model)"
            value={slm}
            onChange={(e) => setSlm(e.target.value)}
          >
            {models?.slm.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} ({m.provider})
              </option>
            )) ?? <option value="qwen3.5-4b">Qwen 3.5 (4B)</option>}
          </Select>

          <Select
            label="LLM (Large Language Model)"
            value={llm}
            onChange={(e) => setLlm(e.target.value)}
          >
            {models?.llm.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} ({m.provider})
              </option>
            )) ?? <option value="llama3.3-70b">Llama 3.3 (70B)</option>}
          </Select>

          <Slider
            label="Number of Samples"
            min={10}
            max={1000}
            step={10}
            value={nSamples}
            onChange={(e) => setNSamples(Number(e.target.value))}
            displayValue={String(nSamples)}
          />

          {architecture === "routing" && (
            <Slider
              label="Confidence Threshold"
              min={0}
              max={1}
              step={0.05}
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
              displayValue={confidenceThreshold.toFixed(2)}
            />
          )}

          {architecture === "ensemble" && (
            <Slider
              label="Number of Models"
              min={2}
              max={5}
              step={1}
              value={nModels}
              onChange={(e) => setNModels(Number(e.target.value))}
              displayValue={String(nModels)}
            />
          )}

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="dry-run"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
              className="h-4 w-4 rounded border-zinc-300"
            />
            <label htmlFor="dry-run" className="text-sm text-zinc-700">
              Dry run (validate config without executing)
            </label>
          </div>

          <Button type="submit" disabled={launch.isPending} className="w-full">
            {launch.isPending ? "Launching..." : "Launch Experiment"}
          </Button>

          {launch.isError && (
            <p className="text-sm text-red-600">
              Error: {(launch.error as Error).message}
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
