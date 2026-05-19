"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { ModePicker } from "@/components/experiment/ModePicker";
import { ModelPicker } from "@/components/experiment/ModelPicker";
import { MultiModelPicker } from "@/components/experiment/MultiModelPicker";
import { ParamControls } from "@/components/experiment/ParamControls";
import {
  useArchitectures,
  useBenchmarks,
  useHosts,
  useLaunchExperiment,
  useModels,
} from "@/hooks/useExperiments";
import type {
  Architecture,
  ArchitectureMode,
  Benchmark,
  ExperimentCreate,
} from "@/types";

const MODE_DEFAULT_ARCH: Record<ArchitectureMode, Architecture> = {
  monolithic: "monolithic",
  hybrid: "routing",
  ensemble: "ensemble",
};

export function ExperimentForm() {
  const router = useRouter();
  const { data: models } = useModels();
  const { data: benchmarks } = useBenchmarks();
  const { data: architectures } = useArchitectures();
  const { data: hostStatus } = useHosts();
  const launch = useLaunchExperiment();

  const [mode, setMode] = useState<ArchitectureMode>("hybrid");
  const [architecture, setArchitecture] = useState<Architecture>("routing");
  const [benchmark, setBenchmark] = useState<Benchmark>("mmlu");
  const [nSamples, setNSamples] = useState(100);
  const [slm, setSlm] = useState("");
  const [llm, setLlm] = useState("");
  const [ensembleSlms, setEnsembleSlms] = useState<string[]>([]);
  const [paramValues, setParamValues] = useState<Record<string, unknown>>({});
  const [dryRun, setDryRun] = useState(false);

  // Architectures available for the selected mode
  const archsForMode = useMemo(() => {
    if (!architectures) return [];
    return architectures.filter((a) => a.mode === mode);
  }, [architectures, mode]);

  const archSpec = architectures?.find((a) => a.id === architecture);

  // When mode changes, snap architecture to a sensible default for that mode.
  useEffect(() => {
    if (!archsForMode.length) return;
    if (!archsForMode.some((a) => a.id === architecture)) {
      const preferred =
        archsForMode.find((a) => a.id === MODE_DEFAULT_ARCH[mode]) ?? archsForMode[0];
      setArchitecture(preferred.id);
    }
  }, [mode, archsForMode, architecture]);

  // When the architecture's spec changes, seed paramValues with defaults.
  useEffect(() => {
    if (!archSpec) return;
    const next: Record<string, unknown> = {};
    for (const p of archSpec.params) {
      next[p.key] = p.default;
    }
    setParamValues(next);
  }, [archSpec?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-pick default SLM/LLM when models load.
  useEffect(() => {
    if (!models) return;
    if (!slm && models.slm.length) {
      const preferred = models.slm.find((m) => m.configured) ?? models.slm[0];
      setSlm(preferred.id);
    }
    if (!llm && models.llm.length) {
      const preferred =
        models.llm.find((m) => m.configured && m.id === "gpt-oss-20b") ??
        models.llm.find((m) => m.configured) ??
        models.llm[0];
      setLlm(preferred.id);
    }
  }, [models, slm, llm]);

  // When the user switches into ensemble mode for the first time, seed it
  // with their single SLM pick so the form is never empty.
  useEffect(() => {
    if (architecture === "ensemble" && ensembleSlms.length === 0 && slm) {
      setEnsembleSlms([slm]);
    }
  }, [architecture, ensembleSlms.length, slm]);

  // Keep n_models in sync with the number of selected SLMs for ensemble.
  useEffect(() => {
    if (architecture !== "ensemble") return;
    if (ensembleSlms.length >= 1) {
      setParamValues((prev) => ({ ...prev, n_models: ensembleSlms.length }));
    }
  }, [architecture, ensembleSlms]);

  const selectedSlmModel = models?.slm.find((m) => m.id === slm);
  const selectedLlmModel = models?.llm.find((m) => m.id === llm);

  function describeHostWarning(): string | null {
    if (!hostStatus) return null;
    const involvedModelIds: string[] = [];
    if (archSpec?.requires_llm && llm) involvedModelIds.push(llm);
    if (archSpec?.requires_slm && slm && architecture !== "ensemble") {
      involvedModelIds.push(slm);
    }
    if (architecture === "ensemble") involvedModelIds.push(...ensembleSlms);

    const sharedHostsTouched = new Set<string>();
    const modelsById = new Map<string, string>(); // model_id -> host_id
    for (const m of [...(models?.slm ?? []), ...(models?.llm ?? [])]) {
      if (m.host_id) modelsById.set(m.id, m.host_id);
    }
    for (const mid of involvedModelIds) {
      const hid = modelsById.get(mid);
      if (!hid) continue;
      const host = hostStatus.hosts.find((h) => h.host_id === hid);
      if (host?.shared) sharedHostsTouched.add(hid);
    }

    if (sharedHostsTouched.size > 1) {
      return "Multiple shared hosts are involved — only one large model per host can be active at a time. Plan model switching accordingly.";
    }
    return null;
  }

  const hostWarning = describeHostWarning();

  const canLaunch = (() => {
    if (!archSpec) return false;
    if (archSpec.requires_llm && !llm) return false;
    if (archSpec.requires_slm) {
      if (architecture === "ensemble") {
        if (ensembleSlms.length === 0) return false;
      } else if (!slm) return false;
    }
    return true;
  })();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!archSpec) return;

    const configOverrides: Record<string, unknown> = { dry_run: dryRun };
    for (const p of archSpec.params) {
      const v = paramValues[p.key];
      if (v !== undefined && v !== null && v !== "") {
        configOverrides[p.key] = v;
      }
    }

    const payload: ExperimentCreate = {
      architecture,
      benchmark,
      n_samples: nSamples,
      slm: archSpec.requires_slm && architecture !== "ensemble" ? slm : null,
      llm: archSpec.requires_llm ? llm : architecture === "ensemble" && paramValues.llm_tiebreak ? llm : null,
      ensemble_slms: architecture === "ensemble" ? ensembleSlms : [],
      config_overrides: configOverrides,
    };

    const result = await launch.mutateAsync(payload);
    router.push(`/experiments/${result.experiment_id}`);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Launch experiment</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Mode */}
          <section className="space-y-2">
            <div className="text-sm font-medium text-zinc-900">1 · Mode</div>
            <ModePicker value={mode} onChange={setMode} />
          </section>

          {/* Architecture under mode */}
          <section className="space-y-2">
            <div className="text-sm font-medium text-zinc-900">2 · Architecture</div>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
              {archsForMode.map((spec) => {
                const active = spec.id === architecture;
                return (
                  <button
                    key={spec.id}
                    type="button"
                    onClick={() => setArchitecture(spec.id)}
                    className={`flex flex-col rounded-md border p-3 text-left transition ${
                      active
                        ? "border-zinc-900 bg-zinc-50"
                        : "border-zinc-200 bg-white hover:border-zinc-400"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-zinc-900">{spec.name}</span>
                      {spec.experimental && (
                        <Badge variant="warning" className="text-[10px]">
                          experimental
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-zinc-600">{spec.description}</p>
                  </button>
                );
              })}
            </div>
          </section>

          {/* Benchmark */}
          <section className="space-y-2">
            <div className="text-sm font-medium text-zinc-900">3 · Benchmark</div>
            <Select
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
                  <option value="custom_stratified">Custom stratified coding</option>
                </>
              )}
            </Select>
          </section>

          {/* Models */}
          <section className="space-y-3">
            <div className="text-sm font-medium text-zinc-900">4 · Models</div>

            {archSpec?.requires_slm && architecture !== "ensemble" && (
              <ModelPicker
                label="SLM"
                description="The small model that drafts answers."
                models={models?.slm ?? []}
                value={slm}
                onChange={setSlm}
              />
            )}

            {architecture === "ensemble" && (
              <MultiModelPicker
                label="Ensemble SLMs"
                description="Each selected SLM contributes one vote."
                models={models?.slm ?? []}
                value={ensembleSlms}
                onChange={setEnsembleSlms}
                min={2}
                max={8}
              />
            )}

            {(archSpec?.requires_llm ||
              (architecture === "ensemble" && Boolean(paramValues.llm_tiebreak))) && (
              <ModelPicker
                label={architecture === "ensemble" ? "Tiebreak LLM" : "LLM"}
                description={
                  architecture === "ensemble"
                    ? "Called only when SLMs don't reach a majority."
                    : "The large model used as fallback / verifier / arbitrator."
                }
                models={models?.llm ?? []}
                value={llm}
                onChange={setLlm}
              />
            )}

            {hostWarning && (
              <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                {hostWarning}
              </div>
            )}
            {selectedSlmModel?.shared_host && selectedSlmModel.is_active_on_host === false && (
              <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                {selectedSlmModel.name} lives on a shared host that currently serves a different
                alias. The run will block until it switches.
              </div>
            )}
            {selectedLlmModel?.shared_host && selectedLlmModel.is_active_on_host === false && (
              <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                {selectedLlmModel.name} lives on a shared host that currently serves a different
                alias. The run will block until it switches.
              </div>
            )}
          </section>

          {/* Sample size */}
          <section className="space-y-2">
            <div className="text-sm font-medium text-zinc-900">5 · Sample size</div>
            <Slider
              label="Samples"
              min={10}
              max={1000}
              step={10}
              value={nSamples}
              onChange={(e) => setNSamples(Number(e.target.value))}
              displayValue={String(nSamples)}
            />
          </section>

          {/* Architecture params */}
          <section className="space-y-2">
            <div className="text-sm font-medium text-zinc-900">6 · Architecture parameters</div>
            <ParamControls
              params={archSpec?.params ?? []}
              values={paramValues}
              onChange={(key, value) =>
                setParamValues((prev) => ({ ...prev, [key]: value }))
              }
            />
          </section>

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
            {launch.isPending ? "Launching…" : "Launch experiment"}
          </Button>

          {launch.isError && (
            <p className="text-sm text-red-600">
              Error: {(launch.error as Error).message}
            </p>
          )}

          {!canLaunch && (
            <p className="text-sm text-zinc-600">
              Pick all required models before launching. Dry run still requires a model selection.
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
