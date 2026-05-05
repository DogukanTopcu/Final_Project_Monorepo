"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ExperimentTable } from "@/components/ExperimentTable";

export default function ExperimentsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Experiments</h1>
        <Link href="/experiments/new">
          <Button>New Experiment</Button>
        </Link>
      </div>
      <ExperimentTable />
    </div>
  );
}
