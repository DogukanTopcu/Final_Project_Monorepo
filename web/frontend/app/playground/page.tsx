"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { cn } from "@/lib/utils";
import { useHosts, useModels } from "@/hooks/useExperiments";
import { api } from "@/lib/api";
import type {
  ModelInfo,
  PlaygroundChatRequest,
  PlaygroundChatResponse,
} from "@/types";

interface ChatTurn {
  id: string;
  role: "user" | "assistant" | "error";
  text: string;
  createdAt: number;
  // assistant-only
  modelId?: string;
  totalLatencyMs?: number;
  modelLatencyMs?: number | null;
  inputTokens?: number;
  outputTokens?: number;
  effectiveMaxTokens?: number;
  costUsd?: number;
  energyKwh?: number | null;
  co2G?: number | null;
}

function formatMs(ms?: number | null): string {
  if (ms == null) return "—";
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)} s`;
  return `${Math.round(ms)} ms`;
}
function formatCost(c?: number | null): string {
  if (c == null) return "—";
  if (c === 0) return "$0";
  if (c < 0.0001) return `$${c.toExponential(2)}`;
  return `$${c.toFixed(6)}`;
}
function formatEnergy(kwh?: number | null): string {
  if (kwh == null || kwh === 0) return "0 Wh";
  const wh = kwh * 1000;
  if (wh < 1) return `${(wh * 1000).toFixed(2)} mWh`;
  return `${wh.toFixed(3)} Wh`;
}
function formatCo2(g?: number | null): string {
  if (g == null || g === 0) return "0 g";
  if (g < 0.001) return `${(g * 1000).toFixed(2)} mg`;
  return `${g.toFixed(3)} g`;
}
function formatTimeOfDay(epochMs: number): string {
  return new Date(epochMs).toLocaleTimeString();
}

export default function PlaygroundPage() {
  const { data: models } = useModels();
  const { data: hostStatus } = useHosts();

  const allModels: ModelInfo[] = useMemo(
    () => [...(models?.slm ?? []), ...(models?.llm ?? [])],
    [models],
  );

  const [modelId, setModelId] = useState("");
  const [prompt, setPrompt] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [temperature, setTemperature] = useState(0);
  const [maxTokens, setMaxTokens] = useState(512);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [modelMenuOpen, setModelMenuOpen] = useState(false);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (modelId) return;
    const preferred = allModels.find((m) => m.configured) ?? allModels[0];
    if (preferred) setModelId(preferred.id);
  }, [allModels, modelId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [turns]);

  // Close model menu when clicking outside
  const modelMenuRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!modelMenuOpen) return;
    const onClick = (e: MouseEvent) => {
      if (!modelMenuRef.current?.contains(e.target as Node)) {
        setModelMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [modelMenuOpen]);

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

  const chat = useMutation({
    mutationFn: async (req: PlaygroundChatRequest) => {
      const t0 = performance.now();
      const res = await api.playgroundChat(req);
      const clientLatency = performance.now() - t0;
      return { res, clientLatency };
    },
    onSuccess: ({ res, clientLatency }, vars) => {
      const turn: ChatTurn = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        role: "assistant",
        text: res.text,
        createdAt: Date.now(),
        modelId: res.model_id,
        totalLatencyMs: clientLatency,
        modelLatencyMs: res.model_latency_ms ?? res.latency_ms,
        inputTokens: res.input_tokens,
        outputTokens: res.output_tokens,
        effectiveMaxTokens: res.effective_max_tokens ?? vars.max_tokens,
        costUsd: res.cost_usd,
        energyKwh: res.energy_kwh,
        co2G: res.co2_g,
      };
      setTurns((t) => [...t, turn]);
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : String(error);
      setTurns((t) => [
        ...t,
        {
          id: `${Date.now()}-err`,
          role: "error",
          text: message,
          createdAt: Date.now(),
        },
      ]);
    },
  });

  const onSend = async () => {
    if (!modelId || !prompt.trim() || chat.isPending) return;
    const userTurn: ChatTurn = {
      id: `${Date.now()}-u`,
      role: "user",
      text: prompt.trim(),
      createdAt: Date.now(),
    };
    setTurns((t) => [...t, userTurn]);
    const payload: PlaygroundChatRequest = {
      model_id: modelId,
      prompt: userTurn.text,
      system: systemPrompt || null,
      temperature,
      max_tokens: maxTokens,
    };
    setPrompt("");
    try {
      await chat.mutateAsync(payload);
    } catch {
      /* error path handled by onError */
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const clearConversation = () => setTurns([]);

  return (
    <div className="mx-auto flex h-[calc(100vh-7rem)] max-w-3xl flex-col">
      {/* Header */}
      <div className="flex items-center justify-between pb-3">
        <div>
          <h1 className="text-2xl font-bold">Playground</h1>
          <p className="text-sm text-zinc-600">
            Test models individually. Each reply includes its own latency, token and emissions
            breakdown.
          </p>
        </div>
        {turns.length > 0 && (
          <button
            type="button"
            onClick={clearConversation}
            className="text-xs text-zinc-500 hover:text-zinc-900"
          >
            Clear conversation
          </button>
        )}
      </div>

      {/* Conversation */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto rounded-md border border-zinc-200 bg-white px-4 py-4"
      >
        {turns.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-zinc-400">
            Start a conversation with{" "}
            <code className="ml-1 rounded bg-zinc-100 px-1 py-0.5">{modelId || "—"}</code>.
          </div>
        ) : (
          <div className="space-y-6">
            {turns.map((turn) =>
              turn.role === "user" ? (
                <UserMessage key={turn.id} turn={turn} />
              ) : turn.role === "error" ? (
                <ErrorMessage key={turn.id} turn={turn} />
              ) : (
                <AssistantMessage key={turn.id} turn={turn} />
              ),
            )}
            {chat.isPending && (
              <div className="text-xs italic text-zinc-500">Thinking…</div>
            )}
          </div>
        )}
      </div>

      {/* Pre-flight warnings */}
      {(hostMismatch || hostUnreachable) && (
        <div
          className={cn(
            "mt-3 rounded-md border px-3 py-2 text-xs",
            hostUnreachable
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-amber-300 bg-amber-50 text-amber-800",
          )}
        >
          {hostUnreachable ? (
            <>
              <strong>{hostForSelected!.label}</strong> is unreachable. Check that the vLLM
              container is running and port 8000 is open.
            </>
          ) : (
            <>
              <strong>{hostForSelected!.label}</strong> currently serves{" "}
              <code className="font-mono">{hostForSelected!.active_model_id}</code>, not{" "}
              <code className="font-mono">{modelId}</code>. The call may 404 unless you switch
              the container first.
            </>
          )}
        </div>
      )}

      {/* Composer */}
      <div className="mt-3 rounded-2xl border border-zinc-300 bg-white shadow-sm focus-within:border-zinc-500">
        {/* Advanced panel (collapsible) */}
        {advancedOpen && (
          <div className="space-y-3 border-b border-zinc-200 px-4 py-3 text-sm">
            <div>
              <label className="text-xs font-medium text-zinc-600">System prompt</label>
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                rows={2}
                placeholder="You are a concise assistant."
                className="mt-1 w-full resize-none rounded-md border border-zinc-200 bg-zinc-50 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
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
          </div>
        )}

        {/* Prompt textarea */}
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={onKeyDown}
          rows={2}
          placeholder={`Message ${modelId || "the model"}…  (Enter to send · Shift+Enter for newline)`}
          className="w-full resize-none rounded-2xl border-0 bg-transparent px-4 pt-3 pb-2 text-sm focus:outline-none"
        />

        {/* Controls row inside composer */}
        <div className="flex items-center justify-between gap-2 px-3 pb-2">
          <div className="flex items-center gap-2">
            {/* Model dropdown chip */}
            <div className="relative" ref={modelMenuRef}>
              <button
                type="button"
                onClick={() => setModelMenuOpen((v) => !v)}
                className="inline-flex items-center gap-1.5 rounded-full border border-zinc-300 bg-zinc-50 px-3 py-1 text-xs font-medium text-zinc-700 hover:border-zinc-500 hover:bg-zinc-100"
              >
                <span>{selectedModel?.name ?? "Pick model"}</span>
                <span className="text-zinc-400">▾</span>
              </button>
              {modelMenuOpen && (
                <ModelMenu
                  models={allModels}
                  value={modelId}
                  onChange={(id) => {
                    setModelId(id);
                    setModelMenuOpen(false);
                  }}
                />
              )}
            </div>

            {/* Advanced toggle */}
            <button
              type="button"
              onClick={() => setAdvancedOpen((v) => !v)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium",
                advancedOpen
                  ? "border-zinc-900 bg-zinc-900 text-white"
                  : "border-zinc-300 bg-zinc-50 text-zinc-700 hover:border-zinc-500 hover:bg-zinc-100",
              )}
            >
              Advanced {advancedOpen ? "▴" : "▾"}
            </button>

            {/* Quick reminders */}
            <span className="hidden text-xs text-zinc-400 md:inline">
              T={temperature.toFixed(2)} · max={maxTokens}
            </span>
          </div>

          <button
            type="button"
            onClick={onSend}
            disabled={!modelId || !prompt.trim() || chat.isPending}
            className={cn(
              "rounded-full px-4 py-1.5 text-sm font-medium transition",
              !modelId || !prompt.trim() || chat.isPending
                ? "cursor-not-allowed bg-zinc-200 text-zinc-400"
                : "bg-zinc-900 text-white hover:bg-zinc-800",
            )}
          >
            {chat.isPending ? "Sending…" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────────

function ModelMenu({
  models,
  value,
  onChange,
}: {
  models: ModelInfo[];
  value: string;
  onChange: (id: string) => void;
}) {
  // Group by host so the user sees the topology.
  const byHost = new Map<string, ModelInfo[]>();
  for (const m of models) {
    const key = m.host_label ?? "Other";
    if (!byHost.has(key)) byHost.set(key, []);
    byHost.get(key)!.push(m);
  }

  return (
    <div className="absolute bottom-full left-0 z-40 mb-2 max-h-80 w-72 overflow-y-auto rounded-lg border border-zinc-200 bg-white p-1.5 shadow-lg">
      {Array.from(byHost.entries()).map(([host, items]) => (
        <div key={host} className="mb-1.5">
          <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
            {host}
          </div>
          {items.map((m) => {
            const active = m.id === value;
            const disabled = !m.configured;
            const inactive = m.shared_host && m.is_active_on_host === false;
            return (
              <button
                key={m.id}
                type="button"
                disabled={disabled}
                onClick={() => onChange(m.id)}
                className={cn(
                  "flex w-full items-center justify-between rounded-md px-2 py-1.5 text-left text-xs",
                  active
                    ? "bg-zinc-900 text-white"
                    : disabled
                      ? "cursor-not-allowed text-zinc-400"
                      : "text-zinc-700 hover:bg-zinc-100",
                )}
              >
                <span className="flex flex-col">
                  <span className="font-medium">{m.name}</span>
                  <span
                    className={cn(
                      "text-[10px]",
                      active ? "text-zinc-300" : "text-zinc-500",
                    )}
                  >
                    {m.id} · {m.tier}
                  </span>
                </span>
                <span className="flex shrink-0 items-center gap-1">
                  {disabled && (
                    <Badge variant="destructive" className="text-[9px]">
                      n/a
                    </Badge>
                  )}
                  {!disabled && inactive && (
                    <Badge variant="warning" className="text-[9px]">
                      switch
                    </Badge>
                  )}
                  {!disabled && m.is_active_on_host && (
                    <Badge variant="success" className="text-[9px]">
                      active
                    </Badge>
                  )}
                </span>
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}

function UserMessage({ turn }: { turn: ChatTurn }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-zinc-900 px-4 py-2 text-sm text-white whitespace-pre-wrap">
        {turn.text}
      </div>
    </div>
  );
}

function ErrorMessage({ turn }: { turn: ChatTurn }) {
  return (
    <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
      <strong>Error.</strong> {turn.text}
    </div>
  );
}

function AssistantMessage({ turn }: { turn: ChatTurn }) {
  return (
    <div className="flex flex-col gap-1">
      {/* Header above message */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-zinc-500">
        <code className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono text-[10px] text-zinc-700">
          {turn.modelId}
        </code>
        <span>
          total <strong className="text-zinc-700">{formatMs(turn.totalLatencyMs)}</strong>
        </span>
        <span>
          model <strong className="text-zinc-700">{formatMs(turn.modelLatencyMs)}</strong>
        </span>
      </div>

      {/* Body */}
      <div className="max-w-[95%] rounded-2xl rounded-bl-sm bg-zinc-100 px-4 py-2 text-sm text-zinc-900 whitespace-pre-wrap">
        {turn.text}
      </div>

      {/* Footer details */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 px-1 text-[11px] text-zinc-500">
        <span>{formatTimeOfDay(turn.createdAt)}</span>
        <span>·</span>
        <span>
          tokens{" "}
          <strong className="text-zinc-700">
            {(turn.inputTokens ?? 0) + (turn.outputTokens ?? 0)}
          </strong>
          {turn.effectiveMaxTokens ? ` / ${turn.effectiveMaxTokens}` : ""}
          {turn.inputTokens != null && turn.outputTokens != null && (
            <span className="text-zinc-400">
              {" "}
              ({turn.inputTokens} in · {turn.outputTokens} out)
            </span>
          )}
        </span>
        <span>·</span>
        <span>
          cost <strong className="text-zinc-700">{formatCost(turn.costUsd)}</strong>
        </span>
        <span>·</span>
        <span>
          energy <strong className="text-zinc-700">{formatEnergy(turn.energyKwh)}</strong>
        </span>
        <span>·</span>
        <span>
          CO₂ <strong className="text-zinc-700">{formatCo2(turn.co2G)}</strong>
        </span>
      </div>
    </div>
  );
}
