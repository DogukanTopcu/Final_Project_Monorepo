"""Emit LaTeX rows for the term-report benchmark tables from results/benchmark_tables."""

import json
import os

TABLES_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "benchmark_tables")
BENCHMARKS = ["mmlu", "arc", "gsm8k", "hellaswag", "truthfulqa"]

ARCH_LABEL = {
    "monolithic": "standalone",
    "multi_agent": "debate",
    "active_oracle": "active\\_oracle",
    "pure_swarm": "pure\\_swarm",
    "entropy_blackboard": "entropy\\_bb",
    "blackboard": "blackboard",
    "ensemble": "ensemble",
    "routing": "routing",
    "speculative": "speculative",
}

SORT_LABEL = {  # plain display label used for alphabetical row ordering
    "monolithic": "standalone",
    "multi_agent": "debate",
    "entropy_blackboard": "entropy_bb",
}


def model_tex(entry):
    arch = entry["architecture"]
    key = entry["model_key"]
    key = key.replace("→", r"$\rightarrow$").replace("+", " + ")
    key = key.replace("[highest_bid]", "(highest bid)").replace("[first_threshold]", "(first threshold)")
    if arch == "multi_agent":
        suffix = " (LLM arb.)" if entry["llm_call_ratio"] else " (SLM arb.)"
        key += suffix
    return key


def main():
    grand_runs = 0
    grand_configs = 0
    for bench in BENCHMARKS:
        path = os.path.join(TABLES_DIR, f"benchmark_{bench}.json")
        with open(path, encoding="utf-8") as f:
            table = json.load(f)
        entries = sorted(
            table["entries"],
            key=lambda e: (SORT_LABEL.get(e["architecture"], e["architecture"]), e["model_key"]),
        )
        n_runs = sum(e["n_experiments"] for e in entries)
        grand_runs += n_runs
        grand_configs += len(entries)
        print(f"% ===== {bench}: {len(entries)} configs, {n_runs} runs =====")
        for e in entries:
            acc = e["accuracy"] * 100
            lat = e["avg_latency_ms"] / 1000
            cost = e["avg_cost_per_sample_usd"]
            co2 = e["avg_co2_per_sample_g"]
            llm = round(e["llm_call_ratio"] * 100)
            eats = e["eats"]
            print(
                f"{ARCH_LABEL[e['architecture']]} & {model_tex(e)} & "
                f"{e['total_samples_evaluated']} & {acc:.1f} & {lat:.1f} & "
                f"{cost:.5f} & {co2:.3f} & {llm} & {eats:.3f} \\\\"
            )
        print()
    print(f"% TOTAL: {grand_configs} configs, {grand_runs} runs across {len(BENCHMARKS)} benchmarks")


if __name__ == "__main__":
    main()
