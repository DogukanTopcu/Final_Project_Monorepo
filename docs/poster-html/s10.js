window.S10 = `
<section class="block">
  <div class="bhead"><div class="num">10</div><div class="btitle">Conclusions</div><div class="line"></div></div>
  <div class="rqs">
    <div class="rq"><div class="tag">RQ1</div><div class="txt">Routing and speculative decoding remain the strongest hybrid performers, while the novel architectures look best on reasoning-heavy tasks: <b>Pure Swarm</b> is the strongest novel result on ARC, and <b>Entropy Blackboard</b> reaches the top GSM8K accuracy.</div></div>
    <div class="rq"><div class="tag">RQ2</div><div class="txt">Low-cost escalation still dominates the EATS frontier on four benchmarks; <b>GSM8K</b> is the one exception, where <b>Pure Swarm</b> becomes the most efficient latest-qualified configuration.</div></div>
    <div class="rq"><div class="tag">RQ3</div><div class="txt">EATS still gives a readable cross-architecture ranking, separating low-cost escalation paths from latency-heavy coordination designs; the best MoE baselines stay competitive but do not lead these latest-qualified comparisons.</div></div>
    <div class="rq"><div class="tag">RQ4</div><div class="txt">The updated measurements still support SLM-first escalation and entropy-aware bidding, but <b>TruthfulQA</b> now favors efficient escalation over debate: routing leads EATS, speculative decoding leads accuracy, and debate no longer beats the task-board variants.</div></div>
  </div>
</section>
`;
