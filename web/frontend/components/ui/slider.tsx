import * as React from "react";
import { cn } from "@/lib/utils";

export interface SliderProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  displayValue?: string;
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ className, label, displayValue, onChange, min, max, step, value, ...rest }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-zinc-700">{label}</label>
            {displayValue !== undefined && (
              <input
                type="number"
                value={value}
                min={min}
                max={max}
                step={step}
                onChange={onChange}
                className="w-20 text-right text-sm text-zinc-500 appearance-none [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none rounded border border-transparent bg-transparent px-1 hover:border-zinc-300 focus:border-zinc-400 focus:outline-none"
              />
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
          onChange={onChange}
          min={min}
          max={max}
          step={step}
          value={value}
          {...rest}
        />
      </div>
    );
  },
);
Slider.displayName = "Slider";

export { Slider };
