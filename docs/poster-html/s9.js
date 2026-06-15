window.EATS_MATRIX = {
  benchmarks: ['MMLU', 'ARC', 'GSM8K', 'HSwag', 'TQA'],
  rows: [
    { arch: 'Routing',               eats: [0.798, 0.904, 0.776, 0.893, 0.854] },
    { arch: 'Speculative',           eats: [0.823, 0.908, 0.725, 0.899, 0.860] },
    { arch: 'Standalone (MoE)',      eats: [0.675, 0.734, 0.663, 0.593, 0.613] },
    { arch: 'Blackboard',            novel: true, eats: [0.685, 0.800, 0.818, 0.672, 0.547] },
    { arch: 'Entropy BB',            novel: true, eats: [0.692, 0.791, 0.826, 0.695, 0.601] },
    { arch: 'Active O.',             novel: true, eats: [0.670, 0.886, 0.750, 0.674, 0.636] },
    { arch: 'Debate POA',            eats: [0.516, 0.659, 0.644, 0.532, 0.517] },
    { arch: 'Pure Swarm',            novel: true, eats: [0.669, 0.818, 0.841, 0.604, 0.606] },
    { arch: 'Ensemble',              eats: [0.403, 0.533, 0.516, 0.429, 0.379] }
  ]
};

window.S9 = `
<section class="block">
  <div class="bhead"><div class="num">11</div><div class="btitle">EATS Landscape</div><div class="line"></div></div>
  <p>Canonical EATS for the latest qualified run of each architecture; the standalone row shows the best MoE baseline on each benchmark.</p>
  <div class="frontier-fig" style="margin-top:6px">
    <div id="eatsMatrix"></div>
    <figcaption>Darker = higher EATS · bold = benchmark winner · tinted rows / <span class="dag">†</span> = novel contribution.</figcaption>
  </div>
</section>
`;
