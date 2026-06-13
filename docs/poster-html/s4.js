window.S4 = `
<section class="block">
  <div class="bhead"><div class="num">4</div><div class="btitle">EATS · Efficiency–Accuracy Trade-off Score</div><div class="line"></div></div>
  <p>Accuracy <span class="mono">α</span> meets cost, latency &amp; energy ratios normalised by the benchmark-specific standalone-LLM baseline.</p>
  <div class="card accent">
    <div class="eq">P = 0.5·<i>C̃</i> + 0.3·<i>L̃</i> + 0.2·<i>Ẽ</i></div>
    <div class="eq" style="padding-top:4px">EATS =
      <span class="frac"><span class="t">α</span><span class="b">α + P</span></span>
    </div>
    <div class="eqnote">C̃ = C/C₀ · L̃ = L/L₀ · Ẽ = E/E₀</div>
  </div>
  <ul class="clean" style="margin-top:14px">
    <li>Increasing in accuracy, decreasing in resource penalty; baseline reduces to <b>α/(α+1)</b> — a clean reference curve.</li>
    <li>Weights reflect deployment priorities: <b>cost &gt; latency &gt; energy</b>.</li>
  </ul>
</section>
`;
