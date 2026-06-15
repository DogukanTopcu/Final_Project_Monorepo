window.S7 = `
<section class="block">
  <div class="bhead"><div class="num">7</div><div class="btitle">Architecture Taxonomy</div><div class="line"></div></div>
  <p>Ten architectures in three families. <span class="dag">†</span> marks novel project contributions introduced in the current study.</p>
  <p>The family progression runs from <strong>internal sparsity</strong> to <strong>explicit coordination</strong> [1][2][3].</p>
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
      <img src="figures/active_oracle.svg" alt="Active Oracle flowchart">
    </div>
    <div class="archcard">
      <h4>Blackboard</h4>
      <img src="figures/black.svg" alt="Blackboard flowchart">
    </div>
  </div>
</section>
`;

window.S7B = `
<div class="section-stack">
  <section class="block">
    <div class="archmini" style="margin-top:16px;">
    <div class="archcard">
      <h4>Entropy Blackboard</h4>
        <img src="figures/entropy_black.svg" alt="Entropy Blackboard flowchart">
    </div>
      <div class="archcard">
        <h4>Pure Swarm</h4>
        <img src="figures/pure_swarm.svg" alt="Pure Swarm flowchart">
      </div>
    </div>
  </section>

  <section class="block">
    <div class="bhead"><div class="num">8</div><div class="btitle">Model Selection &amp; Architecture Pairing</div><div class="line"></div></div>
    <p>We keep the comparison focused on <strong>architecture behavior</strong> by mostly fixing the core hybrid pair: <strong>Gemma4-4B</strong> as worker and <strong>Gemma4-31B</strong> as verifier/sweeper.</p>
    <div class="models-grid">
      <article class="model-card">
        <h4>Selection Rule</h4>
        <p>Models were chosen for <strong>family diversity</strong>, <strong>open-weight reproducibility</strong>, and <strong>MoE coverage</strong>.</p>
      </article>
      <article class="model-card">
        <h4>Best-Working Pairings</h4>
        <p><strong>Routing</strong> and <strong>Speculative</strong> with <strong>Gemma4-4B → Gemma4-31B</strong> gave the strongest EATS on <strong>ARC, HellaSwag, and TruthfulQA</strong>.</p>
      </article>
    </div>
    <div class="reading-notes" style="margin-top:10px;">
      <div class="reading-note"><span>P1</span><p><strong>Routing / Speculative:</strong> <strong>Gemma4-4B → Gemma4-31B</strong> for the strongest quality-efficiency frontier.</p></div>
      <div class="reading-note"><span>P2</span><p><strong>Oracle / Blackboard:</strong> <strong>Gemma4-4B</strong> workers + <strong>Gemma4-31B</strong> sweeper.</p></div>
      <div class="reading-note"><span>P3</span><p><strong>Standalone MoE:</strong> <strong>Qwen3.5-35B-A3B</strong> and <strong>Gemma4-26B-A4B</strong> were the strongest efficient baselines.</p></div>
    </div>
  </section>

  <section class="block">
    <div class="bhead"><div class="num">9</div><div class="btitle">UN SDGs</div><div class="line"></div></div>
    <p>The thesis supports selected <strong>UN Sustainable Development Goals</strong> by making <strong>cost, energy, carbon, and auditability</strong> first-class outputs of architecture evaluation rather than afterthoughts.</p>
    <div class="reading-notes" style="margin-top:6px;">
      <div class="reading-note" style="grid-template-columns:84px 1fr;"><span>SDG 8</span><p><strong>Economic efficiency:</strong> cost-aware comparisons show when smaller or hybrid systems are sufficient, reducing unnecessary frontier-model spend.</p></div>
      <div class="reading-note" style="grid-template-columns:84px 1fr;"><span>SDG 9</span><p><strong>Open infrastructure:</strong> the shared <span class="mono">Query/Response</span> contract and common reporting schema create reusable evaluation infrastructure.</p></div>
      <div class="reading-note" style="grid-template-columns:84px 1fr;"><span>SDG 10</span><p><strong>Reduced inequalities:</strong> hybrid and multi-SLM results show that competitive AI quality can be approached without frontier-scale hardware or cloud budgets.</p></div>
      <div class="reading-note" style="grid-template-columns:84px 1fr;"><span>SDG 12/13</span><p><strong>Responsible energy use:</strong> EATS includes energy and carbon in the main ranking, so wasteful paths are penalised directly.</p></div>
      <div class="reading-note" style="grid-template-columns:84px 1fr;"><span>SDG 16</span><p><strong>Accountable evaluation:</strong> versioned benchmarks, host logs, and transparent metrics make architecture claims easier to audit.</p></div>
    </div>
    <p style="margin-top:10px;">The contribution is therefore <strong>infrastructural</strong>: it helps teams choose capable systems with clearer evidence about <strong>quality, cost, and sustainability</strong>.</p>
  </section>
</div>
`;
