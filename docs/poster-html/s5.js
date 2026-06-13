window.S5 = `
<section class="block">
  <div class="bhead"><div class="num">5</div><div class="btitle">Energy, Carbon &amp; Cost</div><div class="line"></div></div>
  <p>A per-host metrics proxy times each request and samples GPU power via NVIDIA NVML — the boundary sits <em>at the inference host</em>: real power draw, not network overhead.</p>
  <div class="card">
    <div class="eq" style="font-size:22px">
      E = <span class="frac"><span class="t">P<sub>GPU</sub> · Δs</span><span class="b">3.6×10⁶</span></span> kWh
      &nbsp;·&nbsp; CO₂ = <i>k</i>E
      &nbsp;·&nbsp; C = C<sub>API</sub> + r·t
    </div>
    <div class="eqnote">k = 380 gCO₂/kWh · GPU-tier rates $0.75–$6.50 / h</div>
  </div>
</section>
`;
