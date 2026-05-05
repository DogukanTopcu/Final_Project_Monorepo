"use client";

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ResultSummary } from "@/types";

interface MetricsChartProps {
  results: ResultSummary[];
}

const ARCH_COLORS: Record<string, string> = {
  routing: "#3b82f6",
  multi_agent: "#10b981",
  ensemble: "#f59e0b",
};

export function MetricsChart({ results }: MetricsChartProps) {
  const architectures = [...new Set(results.map((r) => r.architecture))];

  const dataByArch = architectures.reduce<Record<string, { accuracy: number; llm_call_ratio: number; name: string }[]>>(
    (acc, arch) => {
      acc[arch] = results
        .filter((r) => r.architecture === arch)
        .map((r) => ({
          accuracy: r.accuracy,
          llm_call_ratio: r.llm_call_ratio ?? 0,
          name: r.experiment_id,
        }));
      return acc;
    },
    {},
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Accuracy vs LLM Call Ratio</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="llm_call_ratio"
              name="LLM Call Ratio"
              domain={[0, 1]}
              label={{ value: "LLM Call Ratio", position: "bottom" }}
            />
            <YAxis
              type="number"
              dataKey="accuracy"
              name="Accuracy"
              domain={[0, 1]}
              label={{ value: "Accuracy", angle: -90, position: "insideLeft" }}
            />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Legend />
            {architectures.map((arch) => (
              <Scatter
                key={arch}
                name={arch.replace("_", " ")}
                data={dataByArch[arch]}
                fill={ARCH_COLORS[arch] ?? "#6b7280"}
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
