"use client";

import {
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ResultSummary } from "@/types";

const ARCH_COLORS: Record<string, string> = {
  monolithic: "#8b5cf6",
  routing: "#3b82f6",
  multi_agent: "#10b981",
  active_oracle: "#14b8a6",
  ensemble: "#f59e0b",
  speculative: "#06b6d4",
  blackboard: "#ef4444",
  entropy_blackboard: "#f97316",
  pure_swarm: "#84cc16",
};

interface ParetoScatterProps {
  title: string;
  xKey: keyof ResultSummary;
  xLabel: string;
  yKey: keyof ResultSummary;
  yLabel: string;
  results: ResultSummary[];
  invertX?: boolean;
}

export function ParetoScatter({
  title,
  xKey,
  xLabel,
  yKey,
  yLabel,
  results,
  invertX,
}: ParetoScatterProps) {
  const architectures = Array.from(new Set(results.map((r) => r.architecture)));

  const dataByArch = architectures.reduce<Record<string, { x: number; y: number; name: string }[]>>(
    (acc, arch) => {
      acc[arch] = results
        .filter((r) => r.architecture === arch)
        .map((r) => ({
          x: Number(r[xKey] ?? 0),
          y: Number(r[yKey] ?? 0),
          name: r.experiment_id,
        }));
      return acc;
    },
    {},
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="x"
              name={xLabel}
              reversed={invertX}
              label={{ value: xLabel, position: "bottom", offset: 0 }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name={yLabel}
              label={{ value: yLabel, angle: -90, position: "insideLeft" }}
            />
            <ZAxis dataKey="name" range={[60, 60]} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Legend />
            {architectures.map((arch) => (
              <Scatter
                key={arch}
                name={arch.replace(/_/g, " ")}
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
