"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSSE } from "@/hooks/useSSE";
import { useCancelExperiment } from "@/hooks/useExperiments";

interface LiveProgressProps {
  experimentId: string;
  enabled: boolean;
  showRoutingLlmRatio?: boolean;
}

export function LiveProgress({
  experimentId,
  enabled,
  showRoutingLlmRatio = false,
}: LiveProgressProps) {
  const { events, lastEvent, isConnected, isReconnecting, error } = useSSE({
    experimentId,
    enabled,
  });
  const cancel = useCancelExperiment();

  const progressEvents = events.filter((e) => e.type === "progress");
  const latest = progressEvents[progressEvents.length - 1];
  const completed = latest?.completed ?? 0;
  const total = latest?.total ?? 1;
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
  const isDone = lastEvent?.type === "complete" || lastEvent?.type === "error";
  let seenProgress = 0;
  const accuracyBySample = new Map<number, number>();
  const llmRatioBySample = new Map<number, number>();
  for (const event of events) {
    if (event.type === "progress") {
      seenProgress = event.completed ?? seenProgress;
    }
    if (event.type === "metric" && event.name === "accuracy" && typeof event.value === "number") {
      const sample = seenProgress || accuracyBySample.size + 1;
      accuracyBySample.set(sample, event.value);
    }
    if (event.type === "metric" && event.name === "llm_call_ratio" && typeof event.value === "number") {
      const sample = seenProgress || llmRatioBySample.size + 1;
      llmRatioBySample.set(sample, event.value);
    }
  }
  const accuracySeries = Array.from(accuracyBySample.entries()).map(([sample, accuracy]) => ({
    sample,
    accuracy,
  }));
  const llmRatioSeries = Array.from(llmRatioBySample.entries()).map(([sample, llmCallRatio]) => ({
    sample,
    llmCallRatio,
  }));
  const lastAccuracy = accuracySeries[accuracySeries.length - 1]?.accuracy ?? null;
  const lastLlmCallRatio = llmRatioSeries[llmRatioSeries.length - 1]?.llmCallRatio ?? null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Live Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="mb-1 flex justify-between text-sm text-zinc-600">
            <span>
              {completed} / {total} samples
            </span>
            <span>{percent}%</span>
          </div>
          <div className="h-3 w-full overflow-hidden rounded-full bg-zinc-200">
            <div
              className="h-full rounded-full bg-zinc-900 transition-all duration-300"
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>

        {latest?.current_query && (
          <p className="truncate text-sm text-zinc-500">
            Current: {latest.current_query}
          </p>
        )}

        {accuracySeries.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm font-medium text-zinc-900">Live accuracy</div>
              <div className="text-sm font-medium text-zinc-700">
                Last accuracy: {lastAccuracy != null ? `${(lastAccuracy * 100).toFixed(1)}%` : "—"}
              </div>
            </div>
            <div className="h-48 w-full rounded-lg border border-zinc-200 bg-white p-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={accuracySeries} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
                  <XAxis
                    type="number"
                    dataKey="sample"
                    domain={[1, Math.max(total, 1)]}
                    allowDecimals={false}
                    tickCount={Math.min(Math.max(total, 2), 6)}
                    tick={{ fontSize: 12, fill: "#71717a" }}
                    label={{ value: "Sample", position: "insideBottom", offset: -4 }}
                  />
                  <YAxis
                    domain={[0, 1]}
                    tickFormatter={(value: number) => `${Math.round(value * 100)}%`}
                    tick={{ fontSize: 12, fill: "#71717a" }}
                    width={44}
                  />
                  <Tooltip
                    cursor={false}
                    formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, "Accuracy"]}
                    labelFormatter={(label: number) => `Sample ${label}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="accuracy"
                    stroke="#18181b"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {showRoutingLlmRatio && llmRatioSeries.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm font-medium text-zinc-900">Live LLM call ratio</div>
              <div className="text-sm font-medium text-zinc-700">
                Current ratio: {lastLlmCallRatio != null ? `${(lastLlmCallRatio * 100).toFixed(1)}%` : "—"}
              </div>
            </div>
            <div className="h-40 w-full rounded-lg border border-amber-200 bg-amber-50/40 p-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={llmRatioSeries} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#fde68a" />
                  <XAxis
                    type="number"
                    dataKey="sample"
                    domain={[1, Math.max(total, 1)]}
                    allowDecimals={false}
                    tickCount={Math.min(Math.max(total, 2), 6)}
                    tick={{ fontSize: 12, fill: "#a16207" }}
                    label={{ value: "Sample", position: "insideBottom", offset: -4 }}
                  />
                  <YAxis
                    domain={[0, 1]}
                    tickFormatter={(value: number) => `${Math.round(value * 100)}%`}
                    tick={{ fontSize: 12, fill: "#a16207" }}
                    width={44}
                  />
                  <Tooltip
                    cursor={false}
                    formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, "LLM call ratio"]}
                    labelFormatter={(label: number) => `Sample ${label}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="llmCallRatio"
                    stroke="#d97706"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {lastEvent?.type === "complete" && lastEvent.metrics && (
          <div className="rounded-lg bg-green-50 p-4">
            <p className="mb-2 font-medium text-green-800">Experiment Complete</p>
            <div className="grid grid-cols-2 gap-2 text-sm text-green-700">
              {Object.entries(lastEvent.metrics).map(([k, v]) => (
                <div key={k}>
                  <span className="font-medium">{k}:</span> {typeof v === "number" ? v.toFixed(4) : v}
                </div>
              ))}
            </div>
          </div>
        )}

        {lastEvent?.type === "complete" && lastEvent.status === "cancelled" && (
          <div className="rounded-lg bg-zinc-100 p-4">
            <p className="font-medium text-zinc-800">Experiment Cancelled</p>
          </div>
        )}

        {lastEvent?.type === "error" && (
          <div className="rounded-lg bg-red-50 p-4">
            <p className="font-medium text-red-800">Error</p>
            <p className="text-sm text-red-600">{lastEvent.message}</p>
          </div>
        )}

        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}

        {!isDone && (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => cancel.mutate(experimentId)}
            disabled={cancel.isPending}
          >
            {cancel.isPending ? "Cancelling..." : "Cancel Experiment"}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
