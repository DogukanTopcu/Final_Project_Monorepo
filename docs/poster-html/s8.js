window.BENCHMARK_PANELS = [
  {
    benchmark: 'MMLU',
    eatsLeader: { label: 'Routing', accuracy: 77.0, eats: 0.825 },
    accuracyLeader: { label: 'gpt-oss-120b', accuracy: 87.0, eats: 0.465 },
    novelLeader: { label: 'Entropy BB', accuracy: 82.0, eats: 0.524 }
  },
  {
    benchmark: 'ARC',
    eatsLeader: { label: 'Routing', accuracy: 91.0, eats: 0.881 },
    accuracyLeader: { label: 'gpt-oss-120b', accuracy: 95.4, eats: 0.488 },
    novelLeader: { label: 'Pure Swarm', accuracy: 92.0, eats: 0.660 }
  },
  {
    benchmark: 'GSM8K',
    eatsLeader: { label: 'Pure Swarm', accuracy: 94.0, eats: 0.684 },
    accuracyLeader: { label: 'Entropy BB', accuracy: 97.0, eats: 0.649 },
    novelLeader: { label: 'Entropy BB', accuracy: 97.0, eats: 0.649 }
  },
  {
    benchmark: 'HellaSwag',
    eatsLeader: { label: 'Routing', accuracy: 90.0, eats: 0.848 },
    accuracyLeader: { label: 'Speculative', accuracy: 92.0, eats: 0.832 },
    novelLeader: { label: 'Entropy BB', accuracy: 84.0, eats: 0.482 }
  },
  {
    benchmark: 'TruthfulQA',
    eatsLeader: { label: 'Routing', accuracy: 85.0, eats: 0.815 },
    accuracyLeader: { label: 'Speculative', accuracy: 88.0, eats: 0.782 },
    novelLeader: { label: 'Entropy BB', accuracy: 75.0, eats: 0.384 }
  }
];

window.S8 = `
<section class="block">
  <div class="bhead"><div class="num">8</div><div class="btitle">Benchmark Readouts</div><div class="line"></div></div>
  <div class="benchmark-panels" id="benchmarkPanels"></div>
</section>
`;
