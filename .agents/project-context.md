# Project Context

## Proje Neden Var?

Bu repo, tez projesi için farklı SLM/LLM cevap üretme mimarilerini ölçülebilir ve tekrarlanabilir şekilde karşılaştırmak amacıyla var.

Temel soru şudur:

> Aynı kullanıcı sorgusu verildiğinde, hangi model/orkestrasyon mimarisi daha doğru, daha hızlı, daha ucuz, daha enerji verimli ve insanlar tarafından daha tercih edilir cevap üretir?

Bu iterasyonda seçilmiş resmi model havuzu şudur:

- Heavy LLM: `kimi-k2.6-1t`, `qwen3.5-397b-a17b`, `gpt-oss-120b`, `llama3.3-70b`
- Light LLM: `qwen3.5-27b`, `gpt-oss-20b`, `gemma4-31b`
- MoE: `qwen3.5-122b-a10b`, `gemma4-26b-a4b`, `qwen3.5-35b-a3b`
- SLM: `gemma4-4b`, `qwen3.5-4b`, `llama3.2-3b`

Normalizasyon notu:

- Kullanıcı kısaltması `Qwen 3.5 (396B)` repo içinde resmi `Qwen/Qwen3.5-397B-A17B` checkpoint'ine normalize edilir.
- Kullanıcı kısaltması `Gemma 4 (4B)` repo içinde `gemma4-4b` alias'ı ve `google/gemma-4-E4B-it` / `gemma4:e4b` runtime adıyla temsil edilir.

Bu yüzden repo yalnızca model çağıran bir uygulama değildir. Aşağıdaki katmanları birlikte kurmaya çalışır:

- Mimari soyutlama: monolithic, routing, multi-agent, ensemble, speculative gibi stratejiler.
- Benchmark altyapısı: MMLU, ARC, HellaSwag, GSM8K, TruthfulQA ve proje özelindeki benchmark'lar.
- Deney koşucusu: aynı konfigürasyonla mimari x benchmark deneylerini çalıştırma.
- Metrik toplama: accuracy, latency, token, cost, EATS, enerji/karbon hedefleri.
- Analiz: sonuç JSON'ları üzerinden istatistik, Pareto ve raporlama.
- MLOps: MLflow tracking, callback ve registry yardımcıları.
- Web/API: deney başlatma/izleme ve insan tercih değerlendirmesi için arayüz hedefi.
- Infrastructure/Docker: yerel ve bulut ortamlarında çalıştırılabilirlik hedefi.
- Training: fine-tuned SLM deneylerini ana architecture karşılaştırmasından ayrı ablation hattı olarak yürütme.

Altyapı notu:

- Küçük ve orta modeller yerelde Ollama veya tek-GPU vLLM ile çalıştırılabilir.
- GCP/prod tarafında repo artık tek generic GPU instance varsaymaz.
- `THESIS_FORCE_VLLM=1` ile aynı repo alias'ları private OpenAI-compatible vLLM endpoint'lerine yönlenebilir.
- Çok büyük modeller (`qwen3.5-397b-a17b`, `kimi-k2.6-1t`) dedicated ve pahalı host sınıfları gerektirir; bunlar dev ortamının doğal uzantısı değildir.

## Kritik Kavramlar

### Query

`core.types.Query`, benchmark veya kullanıcı arayüzünden gelen ortak girdi nesnesidir. Mimari katmanı bu nesneyi alır.

### Response

`core.types.Response`, mimarilerin ortak çıktı sözleşmesidir. Cevap metni, kullanılan model, latency ve maliyet gibi alanları taşır. Bazı planlanan metrikler (`total_tokens`, `energy_kwh`, `co2_g`) henüz bu tipe tam bağlanmış değildir.

### Architecture

`architectures` paketi, aynı `Query` girdisine farklı stratejilerle cevap üretmeyi soyutlar. Amaç şudur: runner aynı benchmark örneğini farklı mimarilere verip ortak `Response` çıktısı alabilsin.

Basit anlatımla:

> Kullanıcı veya benchmark bir soru verir. Architecture katmanı, bu soruya tek modelle mi, router ile mi, birden fazla agent ile mi, ensemble ile mi cevap üretileceğine karar veren strateji katmanıdır. Sonuçta hepsi aynı tipte `Response` döndürmelidir.

### Benchmark

Benchmark, mimarilere verilecek örnekleri ve doğru cevap/evaluation bilgisini sağlar. Otomatik benchmark'larda doğru cevap bellidir. İnsan tercih benchmark'larında doğru cevap yerine kullanıcı/hakem tercihi kaydedilir.

### HumanEval

Bu repodaki `HumanEval`, OpenAI HumanEval kod üretimi benchmark'ı değildir.

Projeye özel anlamı:

1. LLM Arena: Hazır sorulara farklı LLM/mimarilerin verdiği cevapları insanlar değerlendirir.
2. Live Chat Preference: Kullanıcı chat arayüzünde soru sorar, birden fazla architecture cevap üretir, kullanıcı daha iyi cevabı seçer.

Bu benchmark'ın çıktısı pass/fail kod testi değil, insan tercih kaydıdır.

### Custom Stratified Coding

`custom_stratified.py` için hedef, kolay/orta/zor zorluk seviyelerine ayrılmış temel kodlama problemleri dataset'i oluşturmaktır.

Planlanan formatta her örnek en az şu alanlara sahip olmalıdır:

- `id`
- `difficulty`: `easy`, `medium`, `hard`
- `prompt`
- `reference_solution` veya `expected_answer`
- `test_cases`
- `topic`
- `source`

Önerilen minimum pilot: 10 easy, 10 medium, 10 hard.

Önerilen ciddi karşılaştırma seti: en az 150 örnek, yani her zorluk için 50 örnek.

İdeal tez değerlendirmesi: 300 örnek, yani her zorluk için 100 örnek.

### Fine-Tuning / Training

Fine-tune edilmiş SLM'ler ana deneyin parçası olarak değil, ayrı bir ablation ekseni olarak ele alınmalıdır. Ana deney architecture etkisini izole eder; training hattı ise base SLM, fine-tuned SLM ve LLM tradeoff'unu ayrıca ölçer.

Beklenen karşılaştırma:

- Base SLM
- Fine-tuned SLM
- LLM
- Base SLM orchestration
- Fine-tuned SLM orchestration
- Fine-tuned SLM orchestration vs LLM
