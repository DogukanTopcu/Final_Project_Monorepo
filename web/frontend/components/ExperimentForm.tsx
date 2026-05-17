"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { useLaunchExperiment, useModels, useBenchmarks } from "@/hooks/useExperiments";
import type { Benchmark } from "@/types";

export function ExperimentForm() {
  const router = useRouter();
  const { data: models } = useModels();
  const { data: benchmarks } = useBenchmarks();
  const launch = useLaunchExperiment();

  const [benchmark, setBenchmark] = useState<Benchmark>("mmlu");
  const [nSamples, setNSamples] = useState(100);
  const [slm, setSlm] = useState("");
  const [llm, setLlm] = useState("gpt-4o-mini");
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.7);
  const [dryRun, setDryRun] = useState(false);

  useEffect(() => {
    if (!models) {
      return;
    }
    if (models.slm.length > 0 && !models.slm.some((model) => model.id === slm)) {
      setSlm(models.slm[0].id);
    }
    if (!llm && models.llm.some((model) => model.id === "gpt-4o-mini")) {
      setLlm("gpt-4o-mini");
    } else if (models.llm.length > 0 && !models.llm.some((model) => model.id === llm)) {
      const preferredModel =
        models.llm.find((model) => model.id === "gpt-4o-mini") ?? models.llm[0];
      setLlm(preferredModel.id);
    }
  }, [llm, models, slm]);

  const selectedLlmModel = models?.llm.find((model) => model.id === llm);
  const selectedLlmConfigured =
    !models ||
    !selectedLlmModel ||
    (selectedLlmModel.provider === "openai" && models.openai_configured) ||
    (selectedLlmModel.provider === "google" && models.gemini_configured) ||
    selectedLlmModel.provider === "together";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const configOverrides: Record<string, unknown> = { dry_run: dryRun };
    configOverrides.confidence_threshold = confidenceThreshold;

    const result = await launch.mutateAsync({
      architecture: "routing",
      benchmark,
      n_samples: nSamples,
      slm,
      llm,
      config_overrides: configOverrides,
    });
    router.push(`/experiments/${result.experiment_id}`);
  };

  const canLaunch =
    !!slm &&
    !!llm &&
    (!models || dryRun || (models.ollama_reachable && selectedLlmConfigured));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Launch Experiment</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <Select
            label="Architecture"
            value="routing"
            disabled
          >
            <option value="routing">Arch A — Routing</option>
          </Select>

          <div className="space-y-2 rounded-lg border border-zinc-200 bg-zinc-50 p-4">
            <div className="flex flex-wrap gap-2">
              <Badge variant={models?.ollama_reachable ? "success" : "warning"}>
                Ollama {models?.ollama_reachable ? "reachable" : "not reachable"}
              </Badge>
              <Badge variant={models?.slm.length ? "success" : "warning"}>
                {models?.slm.length ? `${models.slm.length} local SLMs found` : "No local SLM found"}
              </Badge>
              <Badge variant={models?.openai_configured ? "success" : "warning"}>
                OpenAI key {models?.openai_configured ? "configured" : "missing"}
              </Badge>
              <Badge variant={models?.gemini_configured ? "success" : "warning"}>
                Gemini key {models?.gemini_configured ? "configured" : "missing"}
              </Badge>
            </div>
            {models?.warnings.map((warning) => (
              <p key={warning} className="text-sm text-amber-700">
                {warning}
              </p>
            ))}
            {!selectedLlmConfigured && (
              <p className="text-sm text-zinc-600">
                Non-dry runs need the API key for the selected fallback model.
              </p>
            )}
          </div>

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
            {models?.slm.length ? (
              models.slm.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.provider})
                </option>
              ))
            ) : (
              <option value="" disabled>
                No local Ollama model available
              </option>
            )}
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
            )) ?? <option value="gpt-4o-mini">GPT-4o Mini</option>}
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

          <Slider
            label="Confidence Threshold"
            min={0}
            max={1}
            step={0.05}
            value={confidenceThreshold}
            onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
            displayValue={confidenceThreshold.toFixed(2)}
          />

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

          <Button type="submit" disabled={launch.isPending || !canLaunch} className="w-full">
            {launch.isPending ? "Launching..." : "Launch Experiment"}
          </Button>

          {launch.isError && (
            <p className="text-sm text-red-600">
              Error: {(launch.error as Error).message}
            </p>
          )}

          {!canLaunch && (
            <p className="text-sm text-zinc-600">
              Launch is enabled once a local Ollama SLM is available. Non-dry runs also require the API key for the selected fallback model.
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
