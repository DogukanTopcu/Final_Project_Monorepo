window.S5 = `
<section class="block">
  <div class="bhead"><div class="num">5</div><div class="btitle">Energy, Carbon &amp; Cost</div><div class="line"></div></div>
  <p>Per-request measurements via GPU power sampling (NVIDIA NVML) at the inference host.</p>
  <div class="card accent">
    <div class="eq"><i>Cost</i> = GPU rate · time</div>
    <div class="eq" style="padding-top:4px"><i>Latency</i> = <i>Δt</i> &nbsp;per request</div>
    <div class="eq" style="padding-top:4px"><i>E</i> = <i>P</i><sub>GPU</sub> · <i>Δt</i> &nbsp;kWh</div>
    <div class="eq" style="padding-top:4px">CO₂ = <i>k</i> · <i>E</i></div>
    <div class="eqnote">k = 380 gCO₂/kWh (EU avg) · E in J ÷ 3.6×10⁶</div>
  </div>
</section>
`;
