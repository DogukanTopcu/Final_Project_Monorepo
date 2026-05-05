"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import Link from "next/link";
import { ArchitectureCompare } from "@/components/ArchitectureCompare";
import { useCompareResults } from "@/hooks/useExperiments";

function CompareContent() {
  const searchParams = useSearchParams();
  const idsParam = searchParams.get("ids") ?? "";
  const ids = idsParam.split(",").filter(Boolean);
  const { data: comparison, isLoading, error } = useCompareResults(ids);

  if (ids.length < 2) {
    return (
      <div className="space-y-4">
        <p className="text-zinc-500">
          Select at least 2 experiments to compare.
        </p>
        <Link href="/results" className="text-zinc-900 underline">
          Back to Results
        </Link>
      </div>
    );
  }

  if (isLoading) {
    return <p className="text-zinc-500">Loading comparison...</p>;
  }

  if (error || !comparison) {
    return <p className="text-red-600">Failed to load comparison data.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/results" className="text-zinc-500 hover:text-zinc-900">
          &larr; Back
        </Link>
        <h1 className="text-3xl font-bold">Compare Experiments</h1>
      </div>
      <ArchitectureCompare comparison={comparison} />
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<p className="text-zinc-500">Loading...</p>}>
      <CompareContent />
    </Suspense>
  );
}
