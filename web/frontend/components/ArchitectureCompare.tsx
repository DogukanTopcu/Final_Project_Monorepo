"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ComparisonResponse } from "@/types";

interface ArchitectureCompareProps {
  comparison: ComparisonResponse;
}

const METRIC_COLORS: Record<string, string> = {
  accuracy: "#3b82f6",
  llm_call_ratio: "#f59e0b",
  eats_score: "#22c55e",
  total_cost: "#ef4444",
};

export function ArchitectureCompare({ comparison }: ArchitectureCompareProps) {
  const metricKeys = new Set<string>();
  for (const m of Object.values(comparison.metrics)) {
    for (const k of Object.keys(m)) {
      metricKeys.add(k);
    }
  }

  const data = comparison.ids.map((id) => ({
    name: id,
    ...comparison.metrics[id],
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Experiment Comparison</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            {[...metricKeys].map((key) => (
              <Bar
                key={key}
                dataKey={key}
                fill={METRIC_COLORS[key] ?? "#6b7280"}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
