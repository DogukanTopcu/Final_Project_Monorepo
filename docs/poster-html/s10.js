window.S10 = `
<section class="block">
  <div class="bhead"><div class="num">10</div><div class="btitle">Conclusions</div><div class="line"></div></div>
  <div class="rqs">
    <div class="rq"><div class="tag">RQ1</div><div class="txt">Collaborative systems are competitive with standalone LLMs; the strongest results come from routing, speculative decoding, and novel coordination on reasoning-heavy tasks.</div></div>
    <div class="rq"><div class="tag">RQ2</div><div class="txt">Hybrid escalation gives the clearest cost and energy gains, while multi-agent coordination usually pays a latency penalty.</div></div>
    <div class="rq"><div class="tag">RQ3</div><div class="txt">EATS gives a consistent cross-architecture ranking: speculative leads four benchmarks, and Pure Swarm leads GSM8K.</div></div>
    <div class="rq"><div class="tag">RQ4</div><div class="txt">The measurements corroborate 8 of 10 SLR trends: SLM-first escalation is the strongest general pattern, while coordination and entropy-aware bidding help on task-specific cases.</div></div>
  </div>
  <div style="margin-top:10px;padding-top:8px;border-top:1.5px solid var(--line);">
    <div style="font-family:var(--font-mono);font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--claret-deep);margin-bottom:5px;">⚠ Limitations</div>
    <ul style="margin:0 0 0 13px;font-size:12.5px;line-height:1.45;color:var(--ink);">
      <li>Single hardware stack (L4 / PRO6000 / H200) — results may not generalise to other GPU tiers or cloud inference endpoints.</li>
      <li>Benchmark scope covers 5 NLP task types; code generation, retrieval-augmented and long-context tasks are not included.</li>
      <li>EATS weights (β = 0.60, λ = 0.40) encode a cost-primary deployment prior; a ±0.1 sensitivity sweep leaves the top-ranked architecture unchanged in 94% of settings (0 dominance reversals).</li>
    </ul>
  </div>
</section>
`;
