# Agent Handoff Prompt

Aşağıdaki prompt, repo üzerinde yeni çalışmaya başlayacak bir agent'a verilebilir.

```text
Bu monorepo, tez kapsamında SLM/LLM tabanlı farklı cevap üretme mimarilerini benchmark, metrik, deney runner, MLflow, analiz, Docker ve infrastructure katmanlarıyla karşılaştırmak için var.

Başlamadan önce repo kökündeki `.agents/README.md`, `.agents/project-context.md`, `.agents/repo-map.md`, `.agents/known-gaps.md` ve `.agents/working-agreement.md` dosyalarını oku.

Kritik notlar:
- Bu repodaki HumanEval, OpenAI HumanEval değildir. UI destekli insan tercih benchmark'ıdır.
- Custom Stratified benchmark, easy/medium/hard kodlama problemleri dataset'i olarak tasarlanmalıdır.
- `eats` benchmark değil metriktir.
- Architecture katmanı aynı Query girdisine farklı stratejilerle cevap üretip ortak Response döndürmelidir.
- Kod değiştirirken mevcut pattern'i takip et, ilgisiz refactor yapma, kullanıcı/başka agent değişikliklerini geri alma.
```

