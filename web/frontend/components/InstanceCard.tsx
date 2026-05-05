"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useStartInstance, useStopInstance } from "@/hooks/useInfrastructure";
import { formatDate } from "@/lib/utils";
import type { InstanceInfo } from "@/types";

interface InstanceCardProps {
  instance: InstanceInfo;
}

const stateVariant: Record<string, "success" | "secondary" | "warning" | "destructive"> = {
  running: "success",
  stopped: "secondary",
  pending: "warning",
  "shutting-down": "warning",
  terminated: "destructive",
};

export function InstanceCard({ instance }: InstanceCardProps) {
  const start = useStartInstance();
  const stop = useStopInstance();
  const isRunning = instance.state === "running";
  const isStopped = instance.state === "stopped";

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg">{instance.name || instance.instance_id}</CardTitle>
        <Badge variant={stateVariant[instance.state] ?? "secondary"}>
          {instance.state}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-zinc-500">Type:</span>{" "}
            <span className="font-mono">{instance.instance_type}</span>
          </div>
          <div>
            <span className="text-zinc-500">ID:</span>{" "}
            <span className="font-mono text-xs">{instance.instance_id}</span>
          </div>
          {instance.public_ip && (
            <div>
              <span className="text-zinc-500">Public IP:</span>{" "}
              <span className="font-mono">{instance.public_ip}</span>
            </div>
          )}
          {instance.private_ip && (
            <div>
              <span className="text-zinc-500">Private IP:</span>{" "}
              <span className="font-mono">{instance.private_ip}</span>
            </div>
          )}
          {instance.launch_time && (
            <div className="col-span-2">
              <span className="text-zinc-500">Launched:</span>{" "}
              {formatDate(instance.launch_time)}
            </div>
          )}
        </div>

        {instance.public_ip && (
          <details className="text-sm">
            <summary className="cursor-pointer text-zinc-600 hover:text-zinc-900">
              SSH Instructions
            </summary>
            <pre className="mt-2 rounded bg-zinc-100 p-2 text-xs">
              ssh -i ~/.ssh/thesis-key.pem ec2-user@{instance.public_ip}
            </pre>
          </details>
        )}

        <div className="flex gap-2">
          {isStopped && (
            <Button
              size="sm"
              onClick={() => start.mutate(instance.instance_id)}
              disabled={start.isPending}
            >
              {start.isPending ? "Starting..." : "Start"}
            </Button>
          )}
          {isRunning && (
            <Button
              size="sm"
              variant="destructive"
              onClick={() => stop.mutate(instance.instance_id)}
              disabled={stop.isPending}
            >
              {stop.isPending ? "Stopping..." : "Stop"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
