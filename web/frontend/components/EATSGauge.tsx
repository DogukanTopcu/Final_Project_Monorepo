"use client";

import { RadialBarChart, RadialBar, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface EATSGaugeProps {
  score: number;
  label?: string;
}

function getColor(score: number): string {
  if (score >= 0.8) return "#22c55e";
  if (score >= 0.6) return "#f59e0b";
  return "#ef4444";
}

export function EATSGauge({ score, label = "EATS Score" }: EATSGaugeProps) {
  const data = [
    { name: "score", value: score * 100, fill: getColor(score) },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-center text-lg">{label}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        <div className="relative h-48 w-48">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="70%"
              outerRadius="100%"
              startAngle={180}
              endAngle={0}
              data={data}
              barSize={16}
            >
              <RadialBar
                dataKey="value"
                cornerRadius={8}
                background={{ fill: "#e5e7eb" }}
              />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center pt-6">
            <span className="text-3xl font-bold" style={{ color: getColor(score) }}>
              {(score * 100).toFixed(1)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
