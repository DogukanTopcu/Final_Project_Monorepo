window.S3 = `
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
      <tr><td>SLM</td><td>NVIDIA L4</td><td class="num-c">24 GB</td><td>gemma4, qwen3.5, llama3.2 (3–4B)</td></tr>
      <tr><td>Mid LLM</td><td>NVIDIA RTX PRO6000</td><td class="num-c">96 GB</td><td>gpt-oss, gemma4, qwen3.5 (20–35B dense + MoE)</td></tr>
      <tr><td>Heavy LLM</td><td>NVIDIA H200</td><td class="num-c">141 GB</td><td>gpt-oss, llama3.3 (70–120B)</td></tr>
    </tbody>
  </table>
</section>
`;
