window.BENCHMARK_PANELS = [
  {
    benchmark: 'MMLU',
    eatsLeader: { label: 'Routing', accuracy: 77.0, eats: 0.825 },
    accuracyLeader: { label: 'gpt-oss-120b', accuracy: 87.0, eats: 0.465 },
    novelLeader: { label: 'Entropy BB', accuracy: 82.0, eats: 0.524 },
    points: [
      { label: 'Active Oracle', penalty: 0.547, accuracy: 72.0, novel: true },
      { label: 'Blackboard', penalty: 0.686, accuracy: 79.0, novel: true },
      { label: 'Ensemble', penalty: 2.473, accuracy: 68.0 },
      { label: 'Entropy BB', penalty: 0.745, accuracy: 82.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 1.000, accuracy: 87.0, baseline: true },
      { label: 'Debate', penalty: 1.346, accuracy: 69.0 },
      { label: 'Pure Swarm', penalty: 0.673, accuracy: 75.0, novel: true },
      { label: 'Routing', penalty: 0.164, accuracy: 77.0 },
      { label: 'Speculative', penalty: 0.194, accuracy: 82.0 }
    ]
  },
  {
    benchmark: 'ARC',
    eatsLeader: { label: 'Routing', accuracy: 91.0, eats: 0.881 },
    accuracyLeader: { label: 'gpt-oss-120b', accuracy: 95.4, eats: 0.488 },
    novelLeader: { label: 'Pure Swarm', accuracy: 92.0, eats: 0.660 },
    points: [
      { label: 'Active Oracle', penalty: 0.186, accuracy: 91.0, novel: true },
      { label: 'Blackboard', penalty: 0.529, accuracy: 92.0, novel: true },
      { label: 'Ensemble', penalty: 2.251, accuracy: 91.0 },
      { label: 'Entropy BB', penalty: 0.568, accuracy: 92.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 1.000, accuracy: 95.4, baseline: true },
      { label: 'Debate', penalty: 1.190, accuracy: 90.0 },
      { label: 'Pure Swarm', penalty: 0.474, accuracy: 92.0, novel: true },
      { label: 'Routing', penalty: 0.123, accuracy: 91.0 },
      { label: 'Speculative', penalty: 0.169, accuracy: 94.0 }
    ]
  },
  {
    benchmark: 'GSM8K',
    eatsLeader: { label: 'Pure Swarm', accuracy: 94.0, eats: 0.684 },
    accuracyLeader: { label: 'Entropy BB', accuracy: 97.0, eats: 0.649 },
    novelLeader: { label: 'Entropy BB', accuracy: 97.0, eats: 0.649 },
    points: [
      { label: 'Active Oracle', penalty: 0.731, accuracy: 92.0, novel: true },
      { label: 'Blackboard', penalty: 0.533, accuracy: 96.0, novel: true },
      { label: 'Ensemble', penalty: 2.676, accuracy: 96.0 },
      { label: 'Entropy BB', penalty: 0.525, accuracy: 97.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 1.000, accuracy: 96.2, baseline: true },
      { label: 'Debate', penalty: 1.397, accuracy: 95.0 },
      { label: 'Pure Swarm', penalty: 0.434, accuracy: 94.0, novel: true },
      { label: 'Routing', penalty: 0.689, accuracy: 95.0 },
      { label: 'Speculative', penalty: 0.913, accuracy: 95.0 }
    ]
  },
  {
    benchmark: 'HellaSwag',
    eatsLeader: { label: 'Routing', accuracy: 90.0, eats: 0.848 },
    accuracyLeader: { label: 'Speculative', accuracy: 92.0, eats: 0.832 },
    novelLeader: { label: 'Entropy BB', accuracy: 84.0, eats: 0.482 },
    points: [
      { label: 'Active Oracle', penalty: 0.431, accuracy: 67.0, novel: true },
      { label: 'Blackboard', penalty: 0.800, accuracy: 77.0, novel: true },
      { label: 'Ensemble', penalty: 2.163, accuracy: 68.0 },
      { label: 'Entropy BB', penalty: 0.903, accuracy: 84.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 1.000, accuracy: 80.6, baseline: true },
      { label: 'Debate', penalty: 1.594, accuracy: 72.0 },
      { label: 'Pure Swarm', penalty: 0.656, accuracy: 65.0, novel: true },
      { label: 'Routing', penalty: 0.161, accuracy: 90.0 },
      { label: 'Speculative', penalty: 0.186, accuracy: 92.0 }
    ]
  },
  {
    benchmark: 'TruthfulQA',
    eatsLeader: { label: 'Routing', accuracy: 85.0, eats: 0.815 },
    accuracyLeader: { label: 'Speculative', accuracy: 88.0, eats: 0.782 },
    novelLeader: { label: 'Entropy BB', accuracy: 75.0, eats: 0.384 },
    points: [
      { label: 'Active Oracle', penalty: 0.851, accuracy: 72.0, novel: true },
      { label: 'Blackboard', penalty: 1.290, accuracy: 68.0, novel: true },
      { label: 'Ensemble', penalty: 2.568, accuracy: 64.0 },
      { label: 'Entropy BB', penalty: 1.205, accuracy: 75.0, novel: true },
      { label: 'gpt-oss-120b', penalty: 1.000, accuracy: 82.4, baseline: true },
      { label: 'Debate', penalty: 1.756, accuracy: 72.0 },
      { label: 'Pure Swarm', penalty: 0.737, accuracy: 67.0, novel: true },
      { label: 'Routing', penalty: 0.193, accuracy: 85.0 },
      { label: 'Speculative', penalty: 0.245, accuracy: 88.0 }
    ]
  }
];

window.S8 = `
<section class="block">
  <div class="bhead"><div class="num">8</div><div class="btitle">Benchmark Readouts</div><div class="line"></div></div>
  <p>Each mini-plot shows accuracy against efficiency penalty, so the strongest trade-offs appear toward the upper-left. <b>E</b> = EATS winner, <b>A</b> = accuracy leader, <b>N</b> = best novel result.</p>
  <div class="benchmark-panels" id="benchmarkPanels"></div>
</section>
`;
