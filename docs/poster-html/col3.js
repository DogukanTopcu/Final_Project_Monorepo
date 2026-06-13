window.COL3 = `
  <section class="block">
    <div class="bhead"><div class="num">8</div><div class="btitle">EATS Frontier per Benchmark</div><div class="line"></div></div>
    <p>Routing &amp; speculative decoding (<span class="mono">gemma4-4b→31b</span>) take the top two EATS positions on <strong>4 of 5 benchmarks</strong>; on GSM8K lean MoE wins as routing escalates only 1% of queries.</p>
    <div class="chart" id="atlasChart"></div>
    <div class="legend">
      <span><i style="background:#8A1538"></i>Routing</span>
      <span><i style="background:#0F7173"></i>Speculative</span>
      <span><i style="background:#B07F2E"></i>Best standalone</span>
    </div>
  </section>

  <section class="block">
    <div class="bhead"><div class="num">9</div><div class="btitle">Key Results</div><div class="line"></div></div>
    <div class="stats">
      <div class="stat"><div class="big">0.884</div><div class="cap">top EATS — <b>Routing on ARC</b><br>91% acc · $0.0005/query</div></div>
      <div class="stat"><div class="big">96%</div><div class="cap"><b>Pure Swarm</b> on ARC<br>with <b>zero</b> LLM calls</div></div>
      <div class="stat"><div class="big">2–15×</div><div class="cap">cost &amp; latency cut<br>vs. standalone LLM</div></div>
    </div>
    <p style="margin-top:16px"><strong>Routing across benchmarks</strong> — escalation is task-dependent, not fixed:</p>
    <table>
      <thead><tr><th>Benchmark</th><th class="num-c">Acc %</th><th class="num-c">EATS</th><th class="num-c">LLM %</th><th class="num-c">$/query</th></tr></thead>
      <tbody>
        <tr><td>MMLU</td><td class="num-c">76.7</td><td class="num-c">0.835</td><td class="num-c">49</td><td class="num-c">0.00074</td></tr>
        <tr class="hl"><td><b>ARC</b></td><td class="num-c">91.0</td><td class="num-c"><b>0.884</b></td><td class="num-c">75</td><td class="num-c">0.00052</td></tr>
        <tr><td>GSM8K</td><td class="num-c">95.0</td><td class="num-c">0.560</td><td class="num-c"><b>1</b></td><td class="num-c">0.00255</td></tr>
        <tr><td>HellaSwag</td><td class="num-c">90.0</td><td class="num-c">0.869</td><td class="num-c">91</td><td class="num-c">0.00061</td></tr>
        <tr><td>TruthfulQA</td><td class="num-c">85.0</td><td class="num-c">0.844</td><td class="num-c">81</td><td class="num-c">0.00057</td></tr>
      </tbody>
    </table>
    <ul class="clean" style="margin-top:14px">
      <li><b>Speculative decoding:</b> 1–5 pts above routing (86% MMLU, 94% ARC) at EATS 0.82–0.86 — verifier rewrites only the divergent suffix.</li>
      <li><b>Four-SLM ensemble:</b> highest raw GSM8K accuracy (96%), but 15–22s parallel latency caps EATS at 0.28–0.39.</li>
      <li><b>Active Oracle</b> underperforms on multiple-choice: sub-queries add cost without recovering the answer chain.</li>
    </ul>
  </section>

  <section class="block">
    <div class="bhead"><div class="num">10</div><div class="btitle">Conclusions</div><div class="line"></div></div>
    <div class="rqs">
      <div class="rq"><div class="tag">RQ1</div><div class="txt">Routing &amp; speculative <b>match best standalone accuracy</b> on ARC, HellaSwag &amp; TruthfulQA; Pure Swarm exceeds every standalone on ARC.</div></div>
      <div class="rq"><div class="tag">RQ2</div><div class="txt">Hybrids cut per-query <b>cost 3–12× and latency 2–7×</b> at near-monolithic accuracy — gains are workload-dependent.</div></div>
      <div class="rq"><div class="tag">RQ3</div><div class="txt">EATS yields a <b>stable single-score ranking</b> of the quality–efficiency frontier across all families.</div></div>
      <div class="rq"><div class="tag">RQ4</div><div class="txt">Measured results corroborate <b>SLM-first escalation</b> &amp; multi-SLM coordination trends from the 54-study review.</div></div>
    </div>
  </section>
`;
