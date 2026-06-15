window.S10 = `
<section class="block">
  <div class="bhead"><div class="num">12</div><div class="btitle">Conclusions</div><div class="line"></div></div>
  <p>The main synthesis is not that one model wins everywhere, but that <strong>the best architecture depends on how much capability you can afford to escalate online</strong>. That is why the poster reports both raw accuracy and EATS rather than collapsing the study into a single leaderboard.</p>
  <div class="rqs">
    <div class="rq"><div class="tag">RQ1</div><div class="txt">Collaborative systems are competitive with standalone LLMs; the strongest results come from routing, speculative decoding, and novel coordination on reasoning-heavy tasks.</div></div>
    <div class="rq"><div class="tag">RQ2</div><div class="txt">Hybrid escalation gives the clearest cost and energy gains, while multi-agent coordination usually pays a latency penalty.</div></div>
    <div class="rq"><div class="tag">RQ3</div><div class="txt">EATS gives a consistent cross-architecture ranking: speculative leads four benchmarks, and Pure Swarm leads GSM8K.</div></div>
    <div class="rq"><div class="tag">RQ4</div><div class="txt">The measurements corroborate 8 of 10 SLR trends: SLM-first escalation is the strongest general pattern, while coordination and entropy-aware bidding help on task-specific cases.</div></div>
  </div>
  <div style="margin-top:10px;padding-top:8px;border-top:1.5px solid var(--line);">
    <div style="font-family:var(--font-mono);font-size:18pt;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--claret-deep);margin-bottom:5px;">Limitations</div>
    <ul style="margin:0 0 0 18px;font-size:18pt;line-height:1.38;color:var(--ink);">
      <li>Single hardware stack (L4 / PRO6000 / H200) — results may not generalise to other GPU tiers or cloud inference endpoints.</li>
      <li>Benchmark scope covers 5 NLP task types; code generation, retrieval-augmented and long-context tasks are not included.</li>
      <li>EATS weights (β = 0.60, λ = 0.40) are fixed after calibration; sensitivity to alternative weight choices is not explored in this study.</li>
    </ul>
  </div>
  <p style="margin-top:12px;">In the full thesis, these findings will be extended with larger sample sizes, pair ablations, and broader task surfaces, but the poster already shows a stable message: <strong>architecture design can buy back a large fraction of frontier-model quality without always paying frontier-model cost</strong>.</p>
</section>
`;
