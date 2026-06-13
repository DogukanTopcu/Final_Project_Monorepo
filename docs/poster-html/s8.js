window.S8 = `
<section class="block">
  <div class="bhead"><div class="num">8</div><div class="btitle">EATS Frontier per Benchmark</div><div class="line"></div></div>
  <p>Routing &amp; speculative decoding (<span class="mono">gemma4-4b→31b</span>) take the top two EATS positions on <strong>4 of 5 benchmarks</strong>; on GSM8K lean MoE wins as routing escalates only 1% of queries.</p>
  <div class="chart" id="atlasChart"></div>
  <div class="legend">
    <span><i style="background:#8A1538"></i>Routing</span>
    <span><i style="background:#0F7173"></i>Speculative</span>
    <span><i style="background:#B07F2E"></i>Best standalone</span>
  </div>
</section>
`;
