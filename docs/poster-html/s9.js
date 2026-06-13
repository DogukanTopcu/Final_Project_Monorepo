window.S9 = `
<section class="block">
  <div class="bhead"><div class="num">9</div><div class="btitle">Key Results</div><div class="line"></div></div>
  <div class="stats">
    <div class="stat"><div class="big">0.884</div><div class="cap">top EATS — <b>Routing on ARC</b><br>91% acc · $0.0005/query</div></div>
    <div class="stat"><div class="big">96%</div><div class="cap"><b>Pure Swarm</b> on ARC<br>with <b>zero</b> LLM calls</div></div>
    <div class="stat"><div class="big">2–15×</div><div class="cap">cost &amp; latency cut<br>vs. standalone LLM</div></div>
  </div>
  <p style="margin-top:16px"><strong>Best EATS vs. best raw accuracy</strong> — benchmark rankings split by objective:</p>
  <table>
    <thead><tr><th>Benchmark</th><th>Top EATS</th><th>Best raw acc</th><th>Read</th></tr></thead>
    <tbody>
      <tr><td>MMLU</td><td><b>Routing</b> 0.835</td><td>Pure Swarm 89.7%</td><td>Efficiency and accuracy leaders diverge</td></tr>
      <tr class="hl"><td><b>ARC</b></td><td><b>Routing</b> 0.884</td><td>Pure Swarm 96.0%</td><td>Hybrids lead EATS; swarm leads accuracy</td></tr>
      <tr><td>GSM8K</td><td><b>gpt-oss-20b / qwen3.5-35b-a3b</b> 0.662</td><td>Blackboard / Entropy BB 97.0%</td><td>Lean standalones win EATS; coordination wins accuracy</td></tr>
      <tr><td>HellaSwag</td><td><b>Routing</b> 0.869</td><td>qwen3.5-35b-a3b 92.6%</td><td>Hybrids approach best standalone</td></tr>
      <tr><td>TruthfulQA</td><td><b>Routing</b> 0.844</td><td>gemma4-31b 93.6%</td><td>Accuracy favors stronger standalone calibration</td></tr>
    </tbody>
  </table>
  <ul class="clean" style="margin-top:14px">
    <li><b>Speculative decoding:</b> 1–5 pts above routing across ARC, HellaSwag, and TruthfulQA at EATS 0.817–0.856 — verifier rewrites only the divergent suffix.</li>
    <li><b>Blackboard family on GSM8K:</b> highest-bid Blackboard and first-threshold Entropy Blackboard both reach <b>97%</b>; Entropy Blackboard does so with only <b>7%</b> sweeper escalation.</li>
    <li><b>Active Oracle</b> underperforms on multiple-choice: sub-queries add cost without recovering the answer chain.</li>
  </ul>
</section>
`;
