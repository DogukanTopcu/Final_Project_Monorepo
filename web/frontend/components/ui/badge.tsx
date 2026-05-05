import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning";
}

const variantStyles: Record<string, string> = {
  default: "bg-zinc-900 text-zinc-50",
  secondary: "bg-zinc-200 text-zinc-900",
  destructive: "bg-red-100 text-red-700",
  outline: "border border-zinc-300 text-zinc-700",
  success: "bg-green-100 text-green-700",
  warning: "bg-amber-100 text-amber-700",
};

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
        variantStyles[variant],
        className,
      )}
      {...props}
    />
  );
}

export { Badge };
