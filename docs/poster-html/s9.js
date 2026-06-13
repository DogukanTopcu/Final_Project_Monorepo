window.S9 = `
<section class="block">
  <div class="bhead"><div class="num">9</div><div class="btitle">Interpretation</div><div class="line"></div></div>
  <div class="reading-notes">
    <div class="reading-note"><span>01</span><p><strong>Hybrids own the efficiency frontier on four benchmarks.</strong> Routing leads MMLU, ARC, HellaSwag, and TruthfulQA; GSM8K is the only benchmark where lean standalones remain more efficient.</p></div>
    <div class="reading-note"><span>02</span><p><strong>Structured reasoning is where the thesis architectures look strongest.</strong> Pure Swarm leads ARC accuracy, and Blackboard-family variants reach the top corrected GSM8K score.</p></div>
    <div class="reading-note"><span>03</span><p><strong>Entropy-aware bidding matters most when confidence is poorly calibrated.</strong> Its clearest gains appear on MMLU, HellaSwag, and TruthfulQA rather than on ARC.</p></div>
    <div class="reading-note"><span>04</span><p><strong>TruthfulQA favors critique over reallocation.</strong> The debate result suggests factual calibration benefits more from adversarial review than from simply handing the prompt to a stronger model later.</p></div>
  </div>
</section>
`;
