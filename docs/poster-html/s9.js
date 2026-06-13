window.S9 = `
<section class="block">
  <div class="bhead"><div class="num">9</div><div class="btitle">Interpretation</div><div class="line"></div></div>
  <div class="reading-notes">
    <div class="reading-note"><span>01</span><p><strong>Hybrids still own the efficiency frontier on four benchmarks.</strong> Routing leads MMLU, ARC, HellaSwag, and TruthfulQA; GSM8K is the only benchmark where Pure Swarm takes the top EATS score.</p></div>
    <div class="reading-note"><span>02</span><p><strong>The novel architectures look strongest on reasoning-heavy tasks.</strong> Pure Swarm is the strongest novel result on ARC, and Entropy Blackboard reaches the top GSM8K accuracy.</p></div>
    <div class="reading-note"><span>03</span><p><strong>Entropy-aware bidding matters most when confidence is poorly calibrated.</strong> Its clearest gains remain on MMLU, HellaSwag, and TruthfulQA, with a smaller effect on ARC.</p></div>
    <div class="reading-note"><span>04</span><p><strong>TruthfulQA now favors efficient escalation rather than debate.</strong> Routing leads EATS, speculative decoding leads accuracy, and the blackboard-family results stay clearly below those two hybrid baselines.</p></div>
  </div>
</section>
`;
