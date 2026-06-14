window.S7 = `
<section class="block">
  <div class="bhead"><div class="num">7</div><div class="btitle">Architecture Taxonomy</div><div class="line"></div></div>
  <p>Ten architectures in three families. <span class="dag">†</span> marks novel project contributions introduced in the current study.</p>
  <table class="zebra">
    <thead><tr><th>Family</th><th>Architecture</th><th>Key mechanism</th></tr></thead>
    <tbody>
      <tr><td><span class="fam">Stand</span></td><td>Single-Model</td><td>direct inference</td></tr>
      <tr><td><span class="fam">Stand</span></td><td>MoE</td><td>internal sparse expert activation</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Routing</td><td>confidence SLM→LLM escalation</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Speculative</td><td>SLM drafts; LLM rewrites suffix</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Debate (POA)</td><td>proponent–opponent–arbitrator</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Active Oracle <span class="dag">†</span></td><td>targeted LLM sub-queries</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Blackboard <span class="dag">†</span></td><td>bid-based task board; LLM sweeper fallback</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Entropy Blackboard <span class="dag">†</span></td><td>uncertainty-penalised bidding</td></tr>
      <tr><td><span class="fam ms">Multi</span></td><td>Ensemble</td><td>majority or confidence-weighted voting</td></tr>
      <tr><td><span class="fam ms">Multi</span></td><td>Pure Swarm <span class="dag">†</span></td><td>SLM-only peer coordination; no LLM online</td></tr>
    </tbody>
  </table>
  <div class="archmini">
    <div class="archcard">
      <h4>Active Oracle</h4>
      <img src="../term_report/sources/active_oracle_simplified.png" alt="Active Oracle flowchart">
    </div>
    <div class="archcard">
      <h4>Pure Swarm</h4>
      <img src="../term_report/sources/blackboard_slms_simplified.png" alt="Pure Swarm flowchart">
    </div>
  </div>
</section>
`;

window.S7B = `
<section class="block">
  <div class="archmini">
    <div class="archcard">
      <h4>Entropy Blackboard</h4>
      <img src="../term_report/sources/blackboard_entropy_based_simplified.png" alt="Entropy Blackboard flowchart">
    </div>
    <div class="archcard">
      <h4>Blackboard</h4>
      <img src="../term_report/sources/blackboard_simplified.png" alt="Blackboard flowchart">
    </div>
  </div>
</section>
`;
