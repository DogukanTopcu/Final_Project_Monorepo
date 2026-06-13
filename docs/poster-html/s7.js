window.S7 = `
<section class="block">
  <div class="bhead"><div class="num">7</div><div class="btitle">Architecture Taxonomy</div><div class="line"></div></div>
  <p>Ten architectures in three families. <span class="dag">†</span> marks novel project contributions introduced in the current study.</p>
  <table>
    <thead><tr><th>Family</th><th>Architecture</th><th>Type</th><th>Key mechanism</th></tr></thead>
    <tbody>
      <tr><td><span class="fam">Stand</span></td><td>Single-Model</td><td>Baseline</td><td>direct inference</td></tr>
      <tr><td><span class="fam">Stand</span></td><td>MoE</td><td>Baseline</td><td>internal sparse expert activation</td></tr>
      <tr class="hl"><td><span class="fam hy">Hybrid</span></td><td><b>Routing</b></td><td>Literature</td><td>confidence SLM→LLM escalation</td></tr>
      <tr class="hl"><td><span class="fam hy">Hybrid</span></td><td><b>Speculative</b></td><td>Literature</td><td>SLM drafts; LLM rewrites suffix</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Debate (POA)</td><td>Literature</td><td>proponent–opponent–arbitrator</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Active Oracle <span class="dag">†</span></td><td>Novel</td><td>targeted LLM sub-queries</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Blackboard <span class="dag">†</span></td><td>Novel</td><td>bid-based task board; LLM sweeper fallback</td></tr>
      <tr><td><span class="fam hy">Hybrid</span></td><td>Entropy Blackboard <span class="dag">†</span></td><td>Novel</td><td>uncertainty-penalised bidding</td></tr>
      <tr><td><span class="fam ms">Multi</span></td><td>Ensemble</td><td>Literature</td><td>majority or confidence-weighted voting</td></tr>
      <tr><td><span class="fam ms">Multi</span></td><td>Pure Swarm <span class="dag">†</span></td><td>Novel</td><td>SLM-only peer coordination; no LLM online</td></tr>
    </tbody>
  </table>
  <div class="archmini">
    <div class="ms">
      <h4>Routing</h4>
      <svg viewBox="0 0 220 120" width="100%">
        <rect x="6" y="46" width="58" height="30" rx="6" fill="#EDE8E1" stroke="#8A1538" stroke-width="2"/>
        <text x="35" y="65" font-size="13" font-family="IBM Plex Mono" text-anchor="middle" fill="#2B2D42">SLM</text>
        <path d="M64 61H110" stroke="#2B2D42" stroke-width="2" fill="none" marker-end="url(#aR)"/>
        <circle cx="118" cy="61" r="13" fill="#0F7173"/>
        <text x="118" y="65" font-size="11" font-family="IBM Plex Mono" text-anchor="middle" fill="#fff">τ?</text>
        <path d="M131 61H180" stroke="#B07F2E" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#aR)"/>
        <rect x="180" y="46" width="34" height="30" rx="6" fill="#8A1538"/>
        <text x="197" y="65" font-size="12" font-family="IBM Plex Mono" text-anchor="middle" fill="#fff">LLM</text>
        <text x="118" y="36" font-size="11" font-family="IBM Plex Mono" text-anchor="middle" fill="#6A6C7E">confident → answer</text>
        <text x="155" y="96" font-size="11" font-family="IBM Plex Mono" text-anchor="middle" fill="#B07F2E">escalate</text>
        <defs><marker id="aR" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0L8 4.5L0 9z" fill="#2B2D42"/></marker></defs>
      </svg>
    </div>
    <div class="ms">
      <h4>Blackboard</h4>
      <svg viewBox="0 0 220 120" width="100%">
        <rect x="60" y="8" width="100" height="26" rx="6" fill="#2B2D42"/>
        <text x="110" y="25" font-size="12" font-family="IBM Plex Mono" text-anchor="middle" fill="#fff">shared board</text>
        <g stroke="#0F7173" stroke-width="2" fill="none">
          <path d="M40 80V46H95V38" marker-end="url(#aB)"/>
          <path d="M110 80V40" marker-end="url(#aB)"/>
          <path d="M180 80V46H125V38" marker-end="url(#aB)"/>
        </g>
        <g font-size="12" font-family="IBM Plex Mono" text-anchor="middle">
          <rect x="18" y="80" width="44" height="26" rx="6" fill="#EDE8E1" stroke="#0F7173" stroke-width="2"/><text x="40" y="97" fill="#2B2D42">SLM</text>
          <rect x="88" y="80" width="44" height="26" rx="6" fill="#EDE8E1" stroke="#0F7173" stroke-width="2"/><text x="110" y="97" fill="#2B2D42">SLM</text>
          <rect x="158" y="80" width="44" height="26" rx="6" fill="#EDE8E1" stroke="#0F7173" stroke-width="2"/><text x="180" y="97" fill="#2B2D42">SLM</text>
        </g>
        <defs><marker id="aB" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0L8 4.5L0 9z" fill="#0F7173"/></marker></defs>
      </svg>
    </div>
  </div>
</section>
`;
