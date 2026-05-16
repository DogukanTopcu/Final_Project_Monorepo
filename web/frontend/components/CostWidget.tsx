"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCosts } from "@/hooks/useInfrastructure";
import { formatCost } from "@/lib/utils";

export function CostWidget() {
  const { data: costs, isLoading } = useCosts();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Estimated Monthly Cost</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-zinc-500">Loading costs...</p>
        ) : costs ? (
          <div className="space-y-3">
            <p className="text-3xl font-bold">{formatCost(costs.total_monthly)}</p>
            <p className="text-sm text-zinc-500">{costs.currency} / month</p>
            {Object.keys(costs.breakdown).length > 0 && (
              <div className="space-y-1">
                {Object.entries(costs.breakdown)
                  .sort(([, a], [, b]) => b - a)
                  .map(([service, amount]) => (
                    <div key={service} className="flex justify-between text-sm">
                      <span className="truncate text-zinc-600">{service}</span>
                      <span className="font-mono">{formatCost(amount)}</span>
                    </div>
                  ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-zinc-500">
            Cost data unavailable. Configure GCP credentials and optional
            billing export to view estimates.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
