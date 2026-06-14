window.S7 = `
<section class="block">
  <div class="bhead"><div class="num">7</div><div class="btitle">Architecture Taxonomy</div><div class="line"></div></div>
  <p>Ten architectures in three families. <span class="dag">†</span> marks novel project contributions introduced in the current study.</p>
  <p>The taxonomy moves from <strong>internal sparsity</strong> and direct inference to <strong>explicit coordination</strong>, making it possible to ask whether efficiency comes from the model itself, from selective escalation, or from multi-step collaboration [1][2][3].</p>
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
      <img src="figures/blackboard.svg" alt="Blackboard flowchart">
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
        <img src="figures/entropy_blackboard.svg" alt="Entropy Blackboard flowchart">
      </div>
      <div class="archcard">
        <h4>Pure Swarm</h4>
        <img src="figures/pure_swarm.svg" alt="Pure Swarm flowchart">
      </div>
    </div>
  </section>

  <section class="block">
    <div class="bhead"><div class="num">8</div><div class="btitle">Model Selection &amp; Architecture Pairing</div><div class="line"></div></div>
    <p>We keep the comparison focused on <strong>architecture behavior</strong> by holding the core hybrid pair mostly fixed: a cheap <strong>Gemma4-4B</strong> worker and a stronger <strong>Gemma4-31B</strong> verifier/sweeper.</p>
    <div class="models-grid">
      <article class="model-card">
        <h4>Selection Rule</h4>
        <p>Models were chosen for <strong>family diversity</strong>, <strong>open-weight reproducibility</strong>, and <strong>MoE coverage</strong>, so sparse-expert baselines can be compared against external orchestration.</p>
      </article>
      <article class="model-card">
        <h4>Best-Working Pairings</h4>
        <p><strong>Routing</strong> and <strong>Speculative</strong> with <strong>Gemma4-4B → Gemma4-31B</strong> gave the strongest EATS on <strong>ARC, HellaSwag, and TruthfulQA</strong>. The most efficient standalone baselines were the <strong>Qwen3.5-35B-A3B</strong> and <strong>Gemma4-26B-A4B</strong> MoE checkpoints.</p>
      </article>
    </div>
  <table class="model-table zebra">
      <thead><tr><th>Architecture</th><th>Models online</th><th>Purpose</th></tr></thead>
      <tbody>
        <tr><td>Routing / Speculative</td><td><b>gemma4-4b → gemma4-31b</b></td><td>Cheap draft/router + stronger verifier for the best quality-efficiency frontier.</td></tr>
        <tr><td>Oracle / Blackboard family</td><td><b>gemma4-4b</b> workers + <b>gemma4-31b</b> sweeper</td><td>Controls for model family while changing only orchestration logic.</td></tr>
        <tr><td>Debate / Ensemble / Pure Swarm</td><td><b>gemma4-4b</b>, <b>qwen3.5-4b</b>, <b>llama3.2-3b</b>, <b>ministral3-3b</b></td><td>Tests whether compact-model diversity and coordination can replace online LLM use.</td></tr>
        <tr><td>Standalone baselines</td><td><b>qwen3.5-35b-a3b</b>, <b>gemma4-26b-a4b</b>, <b>gpt-oss-120b</b>, <b>llama3.3-70b</b></td><td>Separates MoE efficiency from dense-model raw capability.</td></tr>
      </tbody>
    </table>
    <p>Placing the same <strong>Gemma4-4B → Gemma4-31B</strong> pair inside routing, speculative, oracle, and blackboard-style designs is deliberate: the poster compares <strong>control strategies</strong> under a mostly fixed capability pair, while MoE baselines test whether external orchestration still adds value against sparse-expert standalone models [1][2][4].</p>
  </section>
</div>
`;
