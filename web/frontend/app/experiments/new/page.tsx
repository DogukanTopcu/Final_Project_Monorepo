"use client";

import { ExperimentForm } from "@/components/ExperimentForm";

export default function NewExperimentPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold">Launch New Experiment</h1>
      <ExperimentForm />
    </div>
  );
}
