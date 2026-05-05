"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSSE } from "@/hooks/useSSE";
import { useCancelExperiment } from "@/hooks/useExperiments";
import type { SSEEvent } from "@/types";

interface LiveProgressProps {
  experimentId: string;
  enabled: boolean;
}

export function LiveProgress({ experimentId, enabled }: LiveProgressProps) {
  const { events, lastEvent, isConnected, isReconnecting, error } = useSSE({
    experimentId,
    enabled,
  });
  const cancel = useCancelExperiment();

  const progressEvents = events.filter((e) => e.type === "progress");
  const metricEvents = events.filter((e) => e.type === "metric");
  const latest = progressEvents[progressEvents.length - 1];
  const completed = latest?.completed ?? 0;
  const total = latest?.total ?? 1;
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
  const isDone = lastEvent?.type === "complete" || lastEvent?.type === "error";

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Live Progress</CardTitle>
        <div className="flex items-center gap-2">
          {isReconnecting && (
            <Badge variant="warning">Reconnecting...</Badge>
          )}
          {isConnected && <Badge variant="success">Connected</Badge>}
          {error && <Badge variant="destructive">Disconnected</Badge>}
        </div>
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

        {metricEvents.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {metricEvents.map((e: SSEEvent, i: number) => (
              <Badge key={i} variant="outline">
                {e.name}: {e.value?.toFixed(3)}
              </Badge>
            ))}
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
