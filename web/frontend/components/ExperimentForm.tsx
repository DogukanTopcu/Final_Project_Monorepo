"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { useLaunchExperiment, useModels, useBenchmarks } from "@/hooks/useExperiments";
import type { Architecture, Benchmark } from "@/types";

function parseIntegerInput(value: string, fallback: number) {
  const next = Number(value);
  return Number.isFinite(next) ? Math.trunc(next) : fallback;
}

export function ExperimentForm() {
  const router = useRouter();
  const { data: models } = useModels();
  const { data: benchmarks } = useBenchmarks();
  const launch = useLaunchExperiment();

  const [architecture, setArchitecture] = useState<Architecture>("routing");
  const [benchmark, setBenchmark] = useState<Benchmark>("mmlu");
  const [nSamples, setNSamples] = useState(100);
  const [slm, setSlm] = useState("");
  const [llm, setLlm] = useState("");
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.7);
  const [arbitrator, setArbitrator] = useState<"slm" | "llm">("llm");
  const [nDebateRounds, setNDebateRounds] = useState(1);
  const [nModels, setNModels] = useState(3);
  const [voting, setVoting] = useState<"majority" | "weighted">("majority");
  const [llmTiebreak, setLlmTiebreak] = useState(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [slmTemperature, setSlmTemperature] = useState(0);
  const [llmTemperature, setLlmTemperature] = useState(0);
  const [slmMaxTokens, setSlmMaxTokens] = useState(0);
  const [llmMaxTokens, setLlmMaxTokens] = useState(0);
  const [dryRun, setDryRun] = useState(false);

  useEffect(() => {
    if (!models) {
      return;
    }
    if (models.slm.length > 0 && !models.slm.some((model) => model.id === slm)) {
      const preferredSlm = models.slm.find((model) => model.configured) ?? models.slm[0];
      setSlm(preferredSlm.id);
    }
    if (models.llm.length > 0 && !models.llm.some((model) => model.id === llm)) {
      const preferredLlm =
        models.llm.find((model) => model.id === "gpt-oss-20b" && model.configured) ??
        models.llm.find((model) => model.configured) ??
        models.llm[0];
      setLlm(preferredLlm.id);
    }
  }, [llm, models, slm]);

  const selectedSlmModel = models?.slm.find((model) => model.id === slm);
  const selectedLlmModel = models?.llm.find((model) => model.id === llm);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const configOverrides: Record<string, unknown> = { dry_run: dryRun };

    if (architecture === "routing") {
      configOverrides.confidence_threshold = confidenceThreshold;
    }
    if (architecture === "multi_agent") {
      configOverrides.arbitrator = arbitrator;
      configOverrides.n_debate_rounds = nDebateRounds;
    }
    if (architecture === "ensemble") {
      configOverrides.n_models = nModels;
      configOverrides.voting = voting;
      configOverrides.llm_tiebreak = llmTiebreak;
    }
    if (slmTemperature !== 0) {
      configOverrides.slm_temperature = slmTemperature;
    }
    if (llmTemperature !== 0) {
      configOverrides.llm_temperature = llmTemperature;
    }
    if (slmMaxTokens > 0) {
      configOverrides.slm_max_tokens = slmMaxTokens;
    }
    if (llmMaxTokens > 0) {
      configOverrides.llm_max_tokens = llmMaxTokens;
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

  const canLaunch =
    !!slm &&
    !!llm &&
    (!models || dryRun || (!!selectedSlmModel?.configured && !!selectedLlmModel?.configured));

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

          <div className="space-y-2 rounded-lg border border-zinc-200 bg-zinc-50 p-4">
            <div className="flex flex-wrap gap-2">
              <Badge variant={models?.force_vllm ? "success" : "secondary"}>
                Runtime: {models?.runtime_mode ?? "unknown"}
              </Badge>
              <Badge variant={models?.slm.some((model) => model.configured) ? "success" : "warning"}>
                {models?.slm.filter((model) => model.configured).length ?? 0} runnable SLMs
              </Badge>
              <Badge variant={models?.llm.some((model) => model.configured) ? "success" : "warning"}>
                {models?.llm.filter((model) => model.configured).length ?? 0} runnable LLMs
              </Badge>
            </div>
            {models?.warnings.map((warning) => (
              <p key={warning} className="text-sm text-amber-700">
                {warning}
              </p>
            ))}
            {selectedSlmModel && (
              <p className="text-sm text-zinc-600">
                SLM runtime: {selectedSlmModel.runtime_provider}
                {selectedSlmModel.base_url ? ` @ ${selectedSlmModel.base_url}` : ""}
              </p>
            )}
            {selectedLlmModel && (
              <p className="text-sm text-zinc-600">
                LLM runtime: {selectedLlmModel.runtime_provider}
                {selectedLlmModel.base_url ? ` @ ${selectedLlmModel.base_url}` : ""}
              </p>
            )}
          </div>

          <Select
            label="Benchmark"
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value as Benchmark)}
          >
            {benchmarks?.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name} — {item.description}
              </option>
            )) ?? (
              <>
                <option value="mmlu">MMLU</option>
                <option value="arc">ARC</option>
                <option value="hellaswag">HellaSwag</option>
                <option value="gsm8k">GSM8K</option>
                <option value="truthfulqa">TruthfulQA</option>
                <option value="custom_stratified">Custom Stratified Coding</option>
              </>
            )}
          </Select>

          <Select
            label="SLM (Small Language Model)"
            value={slm}
            onChange={(e) => setSlm(e.target.value)}
          >
            {models?.slm.length ? (
              models.slm.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name} ({model.runtime_provider}
                  {model.configured ? "" : " — unavailable"})
                </option>
              ))
            ) : (
              <option value="" disabled>
                No configured SLM available
              </option>
            )}
          </Select>

          <Select
            label="LLM (Fallback / Verifier / Arbitrator)"
            value={llm}
            onChange={(e) => setLlm(e.target.value)}
          >
            {models?.llm.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name} ({model.runtime_provider}
                {model.configured ? "" : " — unavailable"})
              </option>
            )) ?? <option value="llama3.3-70b">Llama 3.3 (70B)</option>}
          </Select>

          <div className="rounded-lg border border-zinc-200 bg-zinc-50">
            <button
              type="button"
              onClick={() => setShowAdvancedSettings((current) => !current)}
              className="flex w-full items-center justify-between px-4 py-3 text-left"
            >
              <div>
                <p className="text-sm font-medium text-zinc-900">Advanced Model Settings</p>
                <p className="text-xs text-zinc-500">
                  Configure randomness and output ceilings separately for SLM and LLM.
                  Leave max tokens at 0 to use auto budgeting.
                </p>
              </div>
              <span className="text-sm text-zinc-500">
                {showAdvancedSettings ? "Hide" : "Show"}
              </span>
            </button>

            {showAdvancedSettings && (
              <div className="space-y-4 border-t border-zinc-200 px-4 py-4">
                <div className="rounded-md border border-zinc-200 bg-white p-4">
                  <div className="mb-3">
                    <p className="text-sm font-medium text-zinc-900">SLM Settings</p>
                    <p className="text-xs text-zinc-500">
                      Temperature controls determinism. Max tokens sets the output ceiling.
                      0 means auto budget.
                    </p>
                  </div>
                  <div className="space-y-4">
                    <Slider
                      label="SLM Temperature"
                      min={0}
                      max={2}
                      step={0.05}
                      value={slmTemperature}
                      onChange={(e) => setSlmTemperature(Number(e.target.value))}
                      displayValue={slmTemperature.toFixed(2)}
                    />
                    <div className="flex flex-col gap-1.5">
                      <div className="flex items-center justify-between">
                        <label htmlFor="slm-max-tokens" className="text-sm font-medium text-zinc-700">
                          SLM Max Tokens
                        </label>
                        <span className="text-sm text-zinc-500">{slmMaxTokens}</span>
                      </div>
                      <input
                        id="slm-max-tokens"
                        type="number"
                        min={0}
                        max={32768}
                        step={1}
                        value={slmMaxTokens}
                        onChange={(e) => setSlmMaxTokens(parseIntegerInput(e.target.value, slmMaxTokens))}
                        className="h-10 rounded-md border border-zinc-300 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
                      />
                    </div>
                  </div>
                </div>

                <div className="rounded-md border border-zinc-200 bg-white p-4">
                  <div className="mb-3">
                    <p className="text-sm font-medium text-zinc-900">LLM Settings</p>
                    <p className="text-xs text-zinc-500">
                      Temperature controls randomness. Max tokens sets the output ceiling.
                      0 means auto budget.
                    </p>
                  </div>
                  <div className="space-y-4">
                    <Slider
                      label="LLM Temperature"
                      min={0}
                      max={2}
                      step={0.05}
                      value={llmTemperature}
                      onChange={(e) => setLlmTemperature(Number(e.target.value))}
                      displayValue={llmTemperature.toFixed(2)}
                    />
                    <div className="flex flex-col gap-1.5">
                      <div className="flex items-center justify-between">
                        <label htmlFor="llm-max-tokens" className="text-sm font-medium text-zinc-700">
                          LLM Max Tokens
                        </label>
                        <span className="text-sm text-zinc-500">{llmMaxTokens}</span>
                      </div>
                      <input
                        id="llm-max-tokens"
                        type="number"
                        min={0}
                        max={32768}
                        step={1}
                        value={llmMaxTokens}
                        onChange={(e) => setLlmMaxTokens(parseIntegerInput(e.target.value, llmMaxTokens))}
                        className="h-10 rounded-md border border-zinc-300 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

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

          {architecture === "multi_agent" && (
            <>
              <Select
                label="Arbitrator"
                value={arbitrator}
                onChange={(e) => setArbitrator(e.target.value as "slm" | "llm")}
              >
                <option value="llm">LLM arbitrator</option>
                <option value="slm">SLM arbitrator</option>
              </Select>
              <Slider
                label="Debate Rounds"
                min={1}
                max={3}
                step={1}
                value={nDebateRounds}
                onChange={(e) => setNDebateRounds(Number(e.target.value))}
                displayValue={String(nDebateRounds)}
              />
            </>
          )}

          {architecture === "ensemble" && (
            <>
              <Slider
                label="Ensemble Size"
                min={2}
                max={5}
                step={1}
                value={nModels}
                onChange={(e) => setNModels(Number(e.target.value))}
                displayValue={String(nModels)}
              />
              <Select
                label="Voting"
                value={voting}
                onChange={(e) => setVoting(e.target.value as "majority" | "weighted")}
              >
                <option value="majority">Majority</option>
                <option value="weighted">Weighted</option>
              </Select>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="llm-tiebreak"
                  checked={llmTiebreak}
                  onChange={(e) => setLlmTiebreak(e.target.checked)}
                  className="h-4 w-4 rounded border-zinc-300"
                />
                <label htmlFor="llm-tiebreak" className="text-sm text-zinc-700">
                  Use LLM tiebreak when ensemble has no majority
                </label>
              </div>
            </>
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
              Launch is enabled once both selected endpoints are runnable. Dry run skips endpoint checks.
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
