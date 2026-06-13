window.S4 = `
<section class="block">
  <div class="bhead"><div class="num">4</div><div class="btitle">EATS · Efficiency–Accuracy Trade-off Score</div><div class="line"></div></div>
  <p>A single score comparing any architecture against the standalone-LLM baseline.</p>
  <div class="card accent">
    <div class="eq">EATS =
      <span class="frac"><span class="t"><i>Accuracy</i></span><span class="b"><i>Accuracy</i> + <i>Penalty</i></span></span>
    </div>
    <div class="eq" style="padding-top:4px;font-size:19px;white-space:nowrap"><i>Penalty</i> = 0.5·<i>Cost</i> + 0.3·<i>Latency</i> + 0.2·<i>Energy</i></div>
    <div class="eqnote">each ÷ standalone-LLM baseline → LLM = 1</div>
  </div>
  <p style="margin-top:10px;font-size:14px;color:var(--mut);text-align:center">0.5 is the theoretical ceiling for the standalone LLM.</p>
</section>
`;
