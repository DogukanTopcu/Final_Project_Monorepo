window.S5 = `
<section class="block">
  <div class="bhead"><div class="num">5</div><div class="btitle">Energy, Carbon &amp; Cost</div><div class="line"></div></div>
  <p>Per-request measurements via GPU power sampling (NVIDIA NVML) at the inference host.</p>
  <div class="formula-grid">
    <div class="formula-item"><i>Cost</i> = GPU rate · time</div>
    <div class="formula-item"><i>E</i> = <i>P</i><sub>GPU</sub> · <i>Δt</i></div>
    <div class="formula-item"><i>Latency</i> = <i>Δt</i> per request</div>
    <div class="formula-item">CO₂ = <i>k</i> · <i>E</i></div>
  </div>
  <div class="formula-note">k = 380 gCO₂/kWh (EU avg) · E in J ÷ 3.6×10⁶</div>
</section>
`;
