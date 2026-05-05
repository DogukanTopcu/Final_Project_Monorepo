import * as React from "react";
import { cn } from "@/lib/utils";

export interface SliderProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  displayValue?: string;
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ className, label, displayValue, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-zinc-700">{label}</label>
            {displayValue && (
              <span className="text-sm text-zinc-500">{displayValue}</span>
            )}
          </div>
        )}
        <input
          type="range"
          ref={ref}
          className={cn(
            "h-2 w-full cursor-pointer appearance-none rounded-lg bg-zinc-200 accent-zinc-900",
            className,
          )}
          {...props}
        />
      </div>
    );
  },
);
Slider.displayName = "Slider";

export { Slider };
