"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { ModelPicker } from "@/components/experiment/ModelPicker";
import { useHosts, useModels } from "@/hooks/useExperiments";
import { api } from "@/lib/api";
import type {
  ModelInfo,
  PlaygroundChatRequest,
  PlaygroundChatResponse,
} from "@/types";

interface HistoryEntry {
  id: string;
  modelId: string;
  prompt: string;
  response: PlaygroundChatResponse;
  createdAt: number;
}

export default function PlaygroundPage() {
  const { data: models } = useModels();
  const { data: hostStatus } = useHosts();
  const [modelId, setModelId] = useState("");
  const [prompt, setPrompt] = useState(
    "Briefly explain why retrieval-augmented generation reduces hallucinations.",
  );
  const [systemPrompt, setSystemPrompt] = useState("");
  const [temperature, setTemperature] = useState(0);
  const [maxTokens, setMaxTokens] = useState(512);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  const allModels: ModelInfo[] = useMemo(
    () => [...(models?.slm ?? []), ...(models?.llm ?? [])],
    [models],
  );

  useEffect(() => {
    if (modelId) return;
    const preferred = allModels.find((m) => m.configured);
    if (preferred) setModelId(preferred.id);
  }, [allModels, modelId]);

  const chat = useMutation({
    mutationFn: (req: PlaygroundChatRequest) => api.playgroundChat(req),
    onSuccess: (response, vars) => {
      setHistory((h) =>
        [
          {
            id: `${Date.now()}`,
            modelId: vars.model_id,
            prompt: vars.prompt,
            response,
            createdAt: Date.now(),
          },
          ...h,
        ].slice(0, 20),
      );
    },
  });

  const submit = async () => {
    if (!modelId || !prompt.trim()) return;
    await chat.mutateAsync({
      model_id: modelId,
      prompt,
      system: systemPrompt || null,
      temperature,
      max_tokens: maxTokens,
    });
  };

  const lastError = chat.isError ? (chat.error as Error).message : null;

  // Pre-flight: detect shared-host mismatches so the user sees a friendly
  // warning instead of a vague 404/502 from the host.
  const selectedModel = allModels.find((m) => m.id === modelId);
  const hostForSelected = hostStatus?.hosts.find(
    (h) => h.host_id === selectedModel?.host_id,
  );
  const hostMismatch =
    selectedModel?.shared_host &&
    hostForSelected &&
    hostForSelected.is_reachable &&
    hostForSelected.active_model_id &&
    hostForSelected.active_model_id !== modelId;
  const hostUnreachable =
    selectedModel?.shared_host && hostForSelected && !hostForSelected.is_reachable;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Playground</h1>
          <p className="text-sm text-zinc-600">
            Send a single prompt to any configured model and see the latency, token and cost
            breakdown.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[20rem_1fr]">
        <Card className="self-start">
          <CardHeader>
            <CardTitle className="text-base">Model</CardTitle>
          </CardHeader>
          <CardContent>
            <ModelPicker
              label="Pick a model"
              models={allModels}
              value={modelId}
              onChange={setModelId}
            />
            <div className="mt-4 space-y-3">
              <Slider
                label="Temperature"
                min={0}
                max={2}
                step={0.05}
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                displayValue={temperature.toFixed(2)}
              />
              <Slider
                label="Max tokens"
                min={32}
                max={4096}
                step={32}
                value={maxTokens}
                onChange={(e) => setMaxTokens(Number(e.target.value))}
                displayValue={String(maxTokens)}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base">Prompt</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <label className="text-xs font-medium text-zinc-600">System (optional)</label>
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                rows={2}
                placeholder="You are a concise assistant."
                className="mt-1 w-full rounded-md border border-zinc-300 bg-white p-2 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-zinc-600">User prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={6}
                className="mt-1 w-full rounded-md border border-zinc-300 bg-white p-2 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
              />
            </div>
            {hostMismatch && (
              <div className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                <strong>{hostForSelected!.label}</strong> currently serves{" "}
                <code className="font-mono">{hostForSelected!.active_model_id}</code>, not{" "}
                <code className="font-mono">{modelId}</code>. Switch the container on the shared
                host first (or enable RTX6000 autoswitch) — otherwise the call will fail with a
                404.
              </div>
            )}
            {hostUnreachable && (
              <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                <strong>{hostForSelected!.label}</strong> is currently unreachable. Check that
                the vLLM container is running and port 8000 is open.
              </div>
            )}
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">
                {modelId ? `Calling: ${modelId}` : "Pick a model first."}
              </span>
              <Button
                type="button"
                onClick={submit}
                disabled={!modelId || !prompt.trim() || chat.isPending}
              >
                {chat.isPending ? "Sending…" : "Send"}
              </Button>
            </div>
            {lastError && (
              <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                {lastError}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent calls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {history.map((entry) => (
              <div
                key={entry.id}
                className="rounded-md border border-zinc-200 bg-white p-3 text-sm"
              >
                <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
                  <Badge variant="secondary">{entry.modelId}</Badge>
                  <span>{new Date(entry.createdAt).toLocaleTimeString()}</span>
                  <span>· {entry.response.latency_ms.toFixed(0)} ms</span>
                  <span>
                    · {entry.response.input_tokens} in / {entry.response.output_tokens} out
                  </span>
                  <span>· ${entry.response.cost_usd.toFixed(6)}</span>
                </div>
                <div className="mb-2 text-xs text-zinc-500">Prompt</div>
                <pre className="whitespace-pre-wrap rounded-md bg-zinc-50 p-2 text-xs text-zinc-700">
                  {entry.prompt}
                </pre>
                <div className="mt-2 mb-2 text-xs text-zinc-500">Response</div>
                <pre className="whitespace-pre-wrap rounded-md bg-zinc-50 p-2 text-xs text-zinc-900">
                  {entry.response.text}
                </pre>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
