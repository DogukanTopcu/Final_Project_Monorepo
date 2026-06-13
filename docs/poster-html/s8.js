window.BENCHMARK_PANELS = [
  {
    benchmark: 'MMLU',
    eatsLeader: { label: 'Routing', accuracy: 76.7, eats: 0.835 },
    accuracyLeader: { label: 'Pure Swarm', accuracy: 89.7, eats: 0.444 },
    novelLeader: { label: 'Entropy BB', accuracy: 83.0, eats: 0.503 },
    insight: 'Efficiency favors the hybrid pair, but raw accuracy shifts to SLM-only coordination.'
  },
  {
    benchmark: 'ARC',
    eatsLeader: { label: 'Routing', accuracy: 91.0, eats: 0.884 },
    accuracyLeader: { label: 'Pure Swarm', accuracy: 96.0, eats: 0.410 },
    novelLeader: { label: 'Pure Swarm', accuracy: 96.0, eats: 0.410 },
    insight: 'Structured science reasoning is the cleanest case for low-cost escalation and swarm consensus.'
  },
  {
    benchmark: 'GSM8K',
    eatsLeader: { label: 'gpt-oss-20b / qwen3.5-35b-a3b tie', accuracy: 94.8, eats: 0.662 },
    accuracyLeader: { label: 'Blackboard / Entropy BB tie', accuracy: 97.0, eats: 0.564 },
    novelLeader: { label: 'Entropy BB', accuracy: 97.0, eats: 0.630 },
    insight: 'Lean standalones win EATS, but task-board coordination reaches the highest corrected accuracy.'
  },
  {
    benchmark: 'HellaSwag',
    eatsLeader: { label: 'Routing', accuracy: 90.0, eats: 0.869 },
    accuracyLeader: { label: 'qwen3.5-35b-a3b', accuracy: 92.6, eats: 0.665 },
    novelLeader: { label: 'Entropy BB', accuracy: 84.0, eats: 0.531 },
    insight: 'Commonsense completion rewards aggressive escalation more than standard bidding alone.'
  },
  {
    benchmark: 'TruthfulQA',
    eatsLeader: { label: 'Routing', accuracy: 85.0, eats: 0.844 },
    accuracyLeader: { label: 'gemma4-31b', accuracy: 93.6, eats: 0.529 },
    novelLeader: { label: 'LLM-arb. Debate', accuracy: 87.0, eats: 0.394 },
    insight: 'Factual calibration benefits more from critique and arbitration than simple reallocation.'
  }
];

window.S8 = `
<section class="block">
  <div class="bhead"><div class="num">8</div><div class="btitle">Benchmark Readouts</div><div class="line"></div></div>
  <p>Each readout compares the <strong>EATS leader</strong>, the <strong>raw-accuracy leader</strong>, and the <strong>strongest thesis architecture</strong> on the same benchmark.</p>
  <div class="benchmark-panels" id="benchmarkPanels"></div>
</section>
`;
