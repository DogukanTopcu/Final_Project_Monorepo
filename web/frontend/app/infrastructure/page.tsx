"use client";

import { InstanceCard } from "@/components/InstanceCard";
import { CostWidget } from "@/components/CostWidget";
import { useInstances } from "@/hooks/useInfrastructure";

export default function InfrastructurePage() {
  const { data: instances, isLoading } = useInstances();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Infrastructure</h1>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold">EC2 Instances</h2>
          {isLoading ? (
            <p className="text-zinc-500">Loading instances...</p>
          ) : instances && instances.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {instances.map((instance) => (
                <InstanceCard key={instance.instance_id} instance={instance} />
              ))}
            </div>
          ) : (
            <p className="text-zinc-500">
              No instances found. Make sure your AWS credentials are configured
              and instances are tagged with Project=thesis.
            </p>
          )}
        </div>

        <div>
          <CostWidget />
        </div>
      </div>
    </div>
  );
}
