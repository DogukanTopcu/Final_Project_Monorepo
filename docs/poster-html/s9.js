window.EATS_MATRIX = {
  benchmarks: ['MMLU', 'ARC', 'GSM8K', 'HSwag', 'TQA'],
  rows: [
    { arch: 'Routing',              eats: [0.835, 0.884, 0.560, 0.869, 0.844] },
    { arch: 'Speculative',          eats: [0.818, 0.853, 0.513, 0.856, 0.817] },
    { arch: 'Standalone (best MoE)', eats: [0.698, 0.738, 0.662, 0.665, 0.577] },
    { arch: 'Blackboard',           novel: true, eats: [0.532, 0.631, 0.626, 0.536, 0.384] },
    { arch: 'Entropy Blackboard',   novel: true, eats: [0.521, 0.622, 0.630, 0.531, 0.462] },
    { arch: 'Active Oracle',        novel: true, eats: [0.392, 0.529, 0.537, 0.404, 0.494] },
    { arch: 'Debate (POA)',         eats: [0.379, 0.451, 0.376, 0.426, 0.394] },
    { arch: 'Pure Swarm',           novel: true, eats: [0.444, 0.410, 0.401, 0.310, 0.245] },
    { arch: 'Ensemble',             eats: [0.299, 0.388, 0.387, 0.316, 0.279] }
  ]
};

window.S9 = `
<section class="block">
  <div class="bhead"><div class="num">9</div><div class="btitle">EATS Landscape</div><div class="line"></div></div>
  <p>EATS for every architecture across the five benchmarks — the full efficiency–accuracy picture in one view.</p>
  <div class="frontier-fig" style="margin-top:6px">
    <div id="eatsMatrix"></div>
    <figcaption>Best configuration per benchmark. Darker = higher EATS · bold = benchmark winner · <span class="dag">†</span> novel contribution.</figcaption>
  </div>
</section>
`;
