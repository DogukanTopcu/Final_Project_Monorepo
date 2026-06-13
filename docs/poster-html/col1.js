window.COL1 = `
  <section class="block">
    <div class="bhead"><div class="num">1</div><div class="btitle">Motivation &amp; Research Questions</div><div class="line"></div></div>
    <p class="lead"><strong>LLMs</strong> deliver state-of-the-art reasoning, but at substantial <strong>latency, monetary, and energy</strong> cost. <strong>SLMs</strong> are cheaper and more data-sovereign, yet still trail frontier models on broad reasoning.</p>
    <p>A companion review of <strong>54 collaborative SLM–LLM studies</strong> reveals a reporting asymmetry: hybrid and multi-agent designs are rising, but <strong>cost and energy are rarely treated as first-class outcomes</strong> alongside accuracy.</p>
    <div class="rqs" style="margin-top:8px">
      <div class="rq"><div class="tag">RQ1</div><div class="txt"><b>Performance.</b> How do collaborative SLM/LLM systems compare with monolithic LLMs on reasoning &amp; classification?</div></div>
      <div class="rq"><div class="tag">RQ2</div><div class="txt"><b>Efficiency.</b> How do hybrid &amp; multi-agent designs affect cost, latency, and energy?</div></div>
      <div class="rq"><div class="tag">RQ3</div><div class="txt"><b>Orchestration.</b> Which routing &amp; division-of-labor mechanisms recur across architectures?</div></div>
      <div class="rq"><div class="tag">RQ4</div><div class="txt"><b>Domain fit.</b> Where do collaborative systems match LLM baselines — and where do they fail?</div></div>
    </div>
  </section>

  <section class="block">
    <div class="bhead"><div class="num">2</div><div class="btitle">Systematic Review</div><div class="line"></div></div>
    <p>PRISMA 2020-guided screening narrowed the literature to the core collaborative corpus that frames our questions.</p>
    <div class="diagram" style="gap:0">
      <div class="dnode"><div class="t">Records identified</div><div class="s">1,200+ database hits</div></div>
      <div class="darrow"><svg width="18" height="24"><path d="M9 0V18M9 24L2 16M9 24L16 16" stroke="currentColor" stroke-width="2.5" fill="none"/></svg></div>
      <div class="dnode"><div class="t">Screened &amp; de-duplicated</div><div class="s">title · abstract · eligibility</div></div>
      <div class="darrow"><svg width="18" height="24"><path d="M9 0V18M9 24L2 16M9 24L16 16" stroke="currentColor" stroke-width="2.5" fill="none"/></svg></div>
      <div class="dnode key"><div class="t">54 studies included</div><div class="s">collaborative SLM–LLM systems</div></div>
    </div>
  </section>

  <section class="block">
    <div class="bhead"><div class="num">3</div><div class="btitle">Measurement-First Platform</div><div class="line"></div></div>
    <p>Every architecture consumes the same <span class="mono">Query</span> and returns the same <span class="mono">Response</span> carrying <strong>accuracy, latency, tokens, cost, energy &amp; CO₂</strong> per query. The architecture layer is the <em>only</em> interchangeable component.</p>
    <div class="diagram" style="margin-top:6px">
      <div class="dnode"><div class="t">Experiment Config</div><div class="s">architecture · benchmark · seed · models</div></div>
      <div class="darrow"><svg width="18" height="22"><path d="M9 0V16M9 22L2 14M9 22L16 14" stroke="currentColor" stroke-width="2.5" fill="none"/></svg></div>
      <div class="dnode"><div class="t">Control Plane</div><div class="s">FastAPI · Next.js UI · runner · host-lock</div></div>
      <div class="darrow"><svg width="18" height="22"><path d="M9 0V16M9 22L2 14M9 22L16 14" stroke="currentColor" stroke-width="2.5" fill="none"/></svg></div>
      <div class="dnode key"><div class="t">Architecture Layer</div><div class="s">routing · speculative · oracle · ensemble · swarm</div></div>
      <div class="darrow"><svg width="18" height="22"><path d="M9 0V16M9 22L2 14M9 22L16 14" stroke="currentColor" stroke-width="2.5" fill="none"/></svg></div>
      <div class="dnode metric"><div class="t">Metrics Proxy + vLLM</div><div class="s">latency · GPU power (NVML) · energy · CO₂ · cost</div></div>
      <div class="darrow"><svg width="18" height="22"><path d="M9 0V16M9 22L2 14M9 22L16 14" stroke="currentColor" stroke-width="2.5" fill="none"/></svg></div>
      <div class="dnode"><div class="t">Scorer → MLflow + Reports</div><div class="s">per-item &amp; aggregate metrics</div></div>
    </div>
    <table style="margin-top:16px">
      <thead><tr><th>Tier</th><th>Host</th><th class="num-c">VRAM</th><th>Models</th></tr></thead>
      <tbody>
        <tr><td>SLM</td><td>GCP L4</td><td class="num-c">24 GB</td><td>Gemma/Qwen/LLaMA 3–4B</td></tr>
        <tr><td>Mid</td><td>RTX PRO 6000</td><td class="num-c">96 GB</td><td>20–35B dense + MoE</td></tr>
        <tr><td>Heavy</td><td>Nebius H200</td><td class="num-c">141 GB</td><td>LLaMA-70B, gpt-oss-120B</td></tr>
      </tbody>
    </table>
  </section>
`;
