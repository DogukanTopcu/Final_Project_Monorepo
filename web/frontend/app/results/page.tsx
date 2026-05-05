"use client";

import { useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricsChart } from "@/components/MetricsChart";
import { useResults } from "@/hooks/useExperiments";
import { formatDate, formatPercent, formatCost } from "@/lib/utils";

export default function ResultsPage() {
  const { data: results, isLoading } = useResults();
  const [selected, setSelected] = useState<string[]>([]);

  const toggleSelect = (id: string) => {
    setSelected((prev) =>
      prev.includes(id)
        ? prev.filter((s) => s !== id)
        : prev.length < 4
          ? [...prev, id]
          : prev,
    );
  };

  if (isLoading) {
    return <p className="text-zinc-500">Loading results...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Results</h1>
        {selected.length >= 2 && (
          <Link href={`/results/compare?ids=${selected.join(",")}`}>
            <Button>Compare Selected ({selected.length})</Button>
          </Link>
        )}
      </div>

      {results && results.length > 0 && <MetricsChart results={results} />}

      <Card>
        <CardHeader>
          <CardTitle>All Results</CardTitle>
        </CardHeader>
        <CardContent>
          {!results?.length ? (
            <p className="text-center text-zinc-500">No results available.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-zinc-200 text-zinc-500">
                    <th className="pb-3 pr-3 font-medium">Select</th>
                    <th className="pb-3 pr-4 font-medium">ID</th>
                    <th className="pb-3 pr-4 font-medium">Architecture</th>
                    <th className="pb-3 pr-4 font-medium">Benchmark</th>
                    <th className="pb-3 pr-4 font-medium">Models</th>
                    <th className="pb-3 pr-4 font-medium">Accuracy</th>
                    <th className="pb-3 pr-4 font-medium">EATS</th>
                    <th className="pb-3 pr-4 font-medium">Cost</th>
                    <th className="pb-3 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r) => (
                    <tr key={r.id} className="border-b border-zinc-100 hover:bg-zinc-50">
                      <td className="py-3 pr-3">
                        <input
                          type="checkbox"
                          checked={selected.includes(r.id)}
                          onChange={() => toggleSelect(r.id)}
                          className="h-4 w-4 rounded border-zinc-300"
                        />
                      </td>
                      <td className="py-3 pr-4 font-mono">{r.experiment_id}</td>
                      <td className="py-3 pr-4 capitalize">{r.architecture.replace("_", " ")}</td>
                      <td className="py-3 pr-4 uppercase">{r.benchmark}</td>
                      <td className="py-3 pr-4">
                        {r.slm} / {r.llm}
                      </td>
                      <td className="py-3 pr-4">{formatPercent(r.accuracy)}</td>
                      <td className="py-3 pr-4">
                        {r.eats_score != null ? formatPercent(r.eats_score) : "—"}
                      </td>
                      <td className="py-3 pr-4">
                        {r.total_cost != null ? formatCost(r.total_cost) : "—"}
                      </td>
                      <td className="py-3">{formatDate(r.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
