"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ResultSummary } from "@/types";

function mean(xs: number[]): number {
  if (xs.length === 0) return NaN;
  return xs.reduce((s, x) => s + x, 0) / xs.length;
}

interface ArchitectureSummaryProps {
  results: ResultSummary[];
}

export function ArchitectureSummary({ results }: ArchitectureSummaryProps) {
  const byArch = new Map<string, ResultSummary[]>();
  for (const r of results) {
    if (!byArch.has(r.architecture)) byArch.set(r.architecture, []);
    byArch.get(r.architecture)!.push(r);
  }

  const rows = Array.from(byArch.entries())
    .map(([arch, items]) => ({
      arch,
      n: items.length,
      acc: mean(items.map((i) => i.accuracy)),
      llmCall: mean(items.map((i) => i.llm_call_ratio ?? 0)),
      latency: mean(items.map((i) => i.avg_latency_ms ?? 0)),
      eats: mean(items.map((i) => i.eats_score ?? 0)),
      cost: mean(items.map((i) => i.total_cost_usd ?? 0)),
      energy: mean(items.map((i) => i.total_energy_kwh ?? 0)),
    }))
    .sort((a, b) => b.acc - a.acc);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Architecture averages</CardTitle>
      </CardHeader>
      <CardContent>
        {rows.length === 0 ? (
          <p className="text-sm text-zinc-500">No matching results.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-200 text-left text-xs uppercase tracking-wider text-zinc-500">
                  <th className="px-3 py-2">Architecture</th>
                  <th className="px-3 py-2">N</th>
                  <th className="px-3 py-2">Accuracy</th>
                  <th className="px-3 py-2">LLM-call rate</th>
                  <th className="px-3 py-2">Latency (ms)</th>
                  <th className="px-3 py-2">EATS</th>
                  <th className="px-3 py-2">Cost ($)</th>
                  <th className="px-3 py-2">Energy (kWh)</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.arch} className="border-b border-zinc-100 last:border-0">
                    <td className="px-3 py-2 font-medium text-zinc-900">
                      {r.arch.replace(/_/g, " ")}
                    </td>
                    <td className="px-3 py-2 text-zinc-600">{r.n}</td>
                    <td className="px-3 py-2 text-zinc-900">
                      {(r.acc * 100).toFixed(1)}%
                    </td>
                    <td className="px-3 py-2 text-zinc-900">
                      {(r.llmCall * 100).toFixed(1)}%
                    </td>
                    <td className="px-3 py-2 text-zinc-900">{r.latency.toFixed(0)}</td>
                    <td className="px-3 py-2 text-zinc-900">{r.eats.toFixed(3)}</td>
                    <td className="px-3 py-2 text-zinc-900">{r.cost.toFixed(4)}</td>
                    <td className="px-3 py-2 text-zinc-900">{r.energy.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
