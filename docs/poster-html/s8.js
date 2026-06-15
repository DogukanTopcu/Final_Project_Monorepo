window.BENCHMARK_PANELS = [
  {
    benchmark: 'MMLU',
    eatsLeader: { label: 'Speculative', accuracy: 82.0, eats: 0.823 },
    accuracyLeader: { label: 'gpt-oss-120b', accuracy: 87.0, eats: 0.675 },
    novelLeader: { label: 'Entropy BB', accuracy: 82.0, eats: 0.692 },
    points: [
      { label: 'Active Oracle', penalty: 0.468, accuracy: 72.0, novel: true },
      { label: 'Blackboard', penalty: 0.591, accuracy: 79.0, novel: true },
      { label: 'Ensemble', penalty: 2.034, accuracy: 68.0 },
      { label: 'Entropy BB', penalty: 0.643, accuracy: 82.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 0.853, accuracy: 87.0, baseline: true },
      { label: 'Debate', penalty: 1.150, accuracy: 69.0 },
      { label: 'Pure Swarm', penalty: 0.554, accuracy: 75.0, novel: true },
      { label: 'Routing', penalty: 0.142, accuracy: 77.0 },
      { label: 'Speculative', penalty: 0.170, accuracy: 82.0 }
    ]
  },
  {
    benchmark: 'ARC',
    eatsLeader: { label: 'Speculative', accuracy: 94.0, eats: 0.908 },
    accuracyLeader: { label: 'gpt-oss-120b', accuracy: 95.4, eats: 0.734 },
    novelLeader: { label: 'Pure Swarm', accuracy: 92.0, eats: 0.818 },
    points: [
      { label: 'Active Oracle', penalty: 0.159, accuracy: 91.0, novel: true },
      { label: 'Blackboard', penalty: 0.454, accuracy: 92.0, novel: true },
      { label: 'Ensemble', penalty: 1.857, accuracy: 91.0 },
      { label: 'Entropy BB', penalty: 0.489, accuracy: 92.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 0.797, accuracy: 95.4, baseline: true },
      { label: 'Debate', penalty: 1.016, accuracy: 90.0 },
      { label: 'Pure Swarm', penalty: 0.391, accuracy: 92.0, novel: true },
      { label: 'Routing', penalty: 0.107, accuracy: 91.0 },
      { label: 'Speculative', penalty: 0.148, accuracy: 94.0 }
    ]
  },
  {
    benchmark: 'GSM8K',
    eatsLeader: { label: 'Pure Swarm', accuracy: 94.0, eats: 0.841 },
    accuracyLeader: { label: 'Entropy BB', accuracy: 97.0, eats: 0.826 },
    novelLeader: { label: 'Entropy BB', accuracy: 97.0, eats: 0.826 },
    points: [
      { label: 'Active Oracle', penalty: 0.646, accuracy: 92.0, novel: true },
      { label: 'Blackboard', penalty: 0.472, accuracy: 96.0, novel: true },
      { label: 'Ensemble', penalty: 2.191, accuracy: 96.0 },
      { label: 'Entropy BB', penalty: 0.465, accuracy: 97.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 1.167, accuracy: 96.2, baseline: true },
      { label: 'Debate', penalty: 1.235, accuracy: 95.0 },
      { label: 'Pure Swarm', penalty: 0.355, accuracy: 94.0, novel: true },
      { label: 'Routing', penalty: 0.609, accuracy: 95.0 },
      { label: 'Speculative', penalty: 0.827, accuracy: 95.0 }
    ]
  },
  {
    benchmark: 'HellaSwag',
    eatsLeader: { label: 'Speculative', accuracy: 92.0, eats: 0.899 },
    accuracyLeader: { label: 'Speculative', accuracy: 92.0, eats: 0.899 },
    novelLeader: { label: 'Entropy BB', accuracy: 84.0, eats: 0.695 },
    points: [
      { label: 'Active Oracle', penalty: 0.315, accuracy: 67.0, novel: true },
      { label: 'Blackboard', penalty: 0.595, accuracy: 77.0, novel: true },
      { label: 'Ensemble', penalty: 1.781, accuracy: 68.0 },
      { label: 'Entropy BB', penalty: 0.680, accuracy: 84.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 1.093, accuracy: 80.6, baseline: true },
      { label: 'Debate', penalty: 1.164, accuracy: 72.0 },
      { label: 'Pure Swarm', penalty: 0.540, accuracy: 65.0, novel: true },
      { label: 'Routing', penalty: 0.121, accuracy: 90.0 },
      { label: 'Speculative', penalty: 0.139, accuracy: 92.0 }
    ]
  },
  {
    benchmark: 'TruthfulQA',
    eatsLeader: { label: 'Speculative', accuracy: 88.0, eats: 0.860 },
    accuracyLeader: { label: 'Speculative', accuracy: 88.0, eats: 0.860 },
    novelLeader: { label: 'Entropy BB', accuracy: 75.0, eats: 0.601 },
    points: [
      { label: 'Active Oracle', penalty: 0.612, accuracy: 72.0, novel: true },
      { label: 'Blackboard', penalty: 0.929, accuracy: 68.0, novel: true },
      { label: 'Ensemble', penalty: 2.077, accuracy: 64.0 },
      { label: 'Entropy BB', penalty: 0.869, accuracy: 75.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 1.037, accuracy: 82.4, baseline: true },
      { label: 'Debate', penalty: 1.263, accuracy: 72.0 },
      { label: 'Pure Swarm', penalty: 0.596, accuracy: 67.0, novel: true },
      { label: 'Routing', penalty: 0.139, accuracy: 85.0 },
      { label: 'Speculative', penalty: 0.177, accuracy: 88.0 }
    ]
  }
];

window.S8 = `
<section class="block">
  <div class="bhead"><div class="num">10</div><div class="btitle">Benchmark Readouts</div><div class="line"></div></div>
  <p>Each mini-plot shows accuracy against efficiency penalty, so the strongest trade-offs appear toward the upper-left. <b>E</b> = EATS winner, <b>A</b> = accuracy leader, <b>N</b> = best novel result.</p>
  <div class="benchmark-panels" id="benchmarkPanels"></div>
</section>
`;
