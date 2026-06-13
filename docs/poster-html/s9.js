window.EATS_MATRIX = {
  benchmarks: ['MMLU', 'ARC', 'GSM8K', 'HSwag', 'TQA'],
  rows: [
    { arch: 'Routing',               eats: [0.825, 0.881, 0.580, 0.848, 0.815] },
    { arch: 'Speculative',           eats: [0.808, 0.848, 0.510, 0.832, 0.782] },
    { arch: 'Standalone (best MoE)', eats: [0.464, 0.488, 0.491, 0.481, 0.459] },
    { arch: 'Blackboard',            novel: true, eats: [0.535, 0.635, 0.643, 0.490, 0.345] },
    { arch: 'Entropy Blackboard',    novel: true, eats: [0.524, 0.618, 0.649, 0.482, 0.384] },
    { arch: 'Active Oracle',         novel: true, eats: [0.568, 0.831, 0.557, 0.608, 0.458] },
    { arch: 'Debate (POA)',          eats: [0.339, 0.431, 0.405, 0.311, 0.291] },
    { arch: 'Pure Swarm',            novel: true, eats: [0.527, 0.660, 0.684, 0.498, 0.476] },
    { arch: 'Ensemble',              eats: [0.216, 0.288, 0.264, 0.239, 0.200] }
  ]
};

window.S9 = `
<section class="block">
  <div class="bhead"><div class="num">9</div><div class="btitle">EATS Landscape</div><div class="line"></div></div>
  <p>Canonical EATS for the latest qualified run of each architecture; the standalone row shows the best MoE baseline on each benchmark.</p>
  <div class="frontier-fig" style="margin-top:6px">
    <div id="eatsMatrix"></div>
    <figcaption>Best configuration per benchmark. Darker = higher EATS · bold = benchmark winner · <span class="dag">†</span> novel contribution.</figcaption>
  </div>
</section>
`;
