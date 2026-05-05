"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useExperiments } from "@/hooks/useExperiments";
import { formatDate, formatPercent } from "@/lib/utils";
import type { ExperimentStatus } from "@/types";

const statusVariant: Record<ExperimentStatus, "success" | "warning" | "destructive" | "secondary" | "default"> = {
  completed: "success",
  running: "warning",
  queued: "secondary",
  failed: "destructive",
  cancelled: "default",
};

export function ExperimentTable() {
  const { data: experiments, isLoading } = useExperiments();

  if (isLoading) {
    return <p className="text-zinc-500">Loading experiments...</p>;
  }

  if (!experiments?.length) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-zinc-500">
          No experiments yet.{" "}
          <Link href="/experiments/new" className="text-zinc-900 underline">
            Launch one
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Experiments</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-zinc-200 text-zinc-500">
                <th className="pb-3 pr-4 font-medium">ID</th>
                <th className="pb-3 pr-4 font-medium">Architecture</th>
                <th className="pb-3 pr-4 font-medium">Benchmark</th>
                <th className="pb-3 pr-4 font-medium">Models</th>
                <th className="pb-3 pr-4 font-medium">Status</th>
                <th className="pb-3 pr-4 font-medium">Accuracy</th>
                <th className="pb-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {experiments.map((exp) => (
                <tr key={exp.experiment_id} className="border-b border-zinc-100 hover:bg-zinc-50">
                  <td className="py-3 pr-4">
                    <Link
                      href={`/experiments/${exp.experiment_id}`}
                      className="font-mono text-zinc-900 underline-offset-2 hover:underline"
                    >
                      {exp.experiment_id}
                    </Link>
                  </td>
                  <td className="py-3 pr-4 capitalize">{exp.architecture.replace("_", " ")}</td>
                  <td className="py-3 pr-4 uppercase">{exp.benchmark}</td>
                  <td className="py-3 pr-4">
                    {exp.slm} / {exp.llm}
                  </td>
                  <td className="py-3 pr-4">
                    <Badge variant={statusVariant[exp.status]}>{exp.status}</Badge>
                  </td>
                  <td className="py-3 pr-4">
                    {exp.metrics?.accuracy != null ? formatPercent(exp.metrics.accuracy) : "—"}
                  </td>
                  <td className="py-3">{formatDate(exp.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
