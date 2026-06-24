window.S4 = `
<section class="block">
  <div class="bhead"><div class="num">4</div><div class="btitle">EATS · Efficiency–Accuracy Trade-off Score</div><div class="line"></div></div>
  <p>A single score comparing any architecture against the standalone-LLM baseline.</p>
  <div class="card accent">
    <div class="eats-formula">
      <div class="eats-main">
        <span class="lhs">EATS</span> =
        <span class="frac">
          <span class="t"><i>Accuracy</i></span>
          <span class="b"><i>Accuracy</i> + <span class="sig">λ</span>·<i>P</i><sub>efficiency</sub> + <span class="sig">β</span>·<i>P</i><sub>accuracy</sub></span>
        </span>
      </div>
      <div class="eats-defs">
        <div class="eats-def"><i>P</i><sub>efficiency</sub> = 0.65·<i>Cost</i> + 0.20·<i>Latency</i> + 0.15·<i>Energy</i></div>
        <div class="eats-def"><i>P</i><sub>accuracy</sub> = 1 − <i>Accuracy</i></div>
      </div>
      <div class="eats-params">
        <span>β = 0.60</span>
        <span>λ = 0.40</span>
      </div>
    </div>
    <div class="eqnote">all terms normalised per standalone-LLM baseline · weights (β = 0.60, λ = 0.40) set from a cost-primary deployment prior; rankings robust to ±0.1 perturbation</div>
  </div>
</section>
`;
