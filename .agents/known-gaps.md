# Known Gaps and Backlog

Bu dosya, repo extraction sırasında görülen yapılacak işleri merkezi olarak tutar. Öncelik sırası kesin roadmap değildir; yeni işlerde en ilgili bölümü kontrol edin.

## Kritik Kavramsal Düzeltmeler

- `HumanEval`, OpenAI HumanEval değildir. UI destekli insan tercih benchmark'ıdır.
- `custom_stratified.py`, MMLU/GSM8K karışımı değil, easy/medium/hard temel kodlama problemleri dataset'i olmalıdır.
- `eats`, benchmark değil metriktir. UI/API listelerinde benchmark gibi geçiyorsa düzeltilmelidir.

## Architecture Uyumluluğu

- Tüm architecture sınıfları ortak constructor ve `generate(query)` sözleşmesine hizalanmalı.
- Runner'ın `slm`, `llm`, `task_type` parametreleri ile architecture constructor imzaları eşleştirilmeli.
- `Response` tipine ihtiyaç duyulan alanlar eklenmeli veya architecture çıktıları mevcut tipe göre sadeleştirilmeli.
- vLLM tabanlı sınıfların `total_tokens` gibi alanları type contract ile uyumlu hale getirilmeli.
- `multi_agent.n_rounds` gerçek davranışa bağlanmalı veya kaldırılmalı.
- `ensemble` için paralel/sequential davranış açıkça seçilmeli ve dokümante edilmeli.

## Benchmark İşleri

- `humaneval.py`, insan tercih benchmark veri modeliyle yeniden ele alınmalı.
- LLM Arena ve Live Chat Preference kayıt formatları netleştirilmeli.
- `custom_stratified.py`, zorluk seviyeli kodlama dataset loader/evaluator haline getirilmeli.
- Custom coding dataset için pilot set oluşturulmalı: 10 easy, 10 medium, 10 hard.
- Ciddi karşılaştırma için minimum 150 örnek hedeflenmeli.
- İdeal tez seti için 300 örnek hedeflenmeli.
- Benchmark registry, yeni benchmark isimleriyle uyumlu hale getirilmeli.

## Core Type and Config İşleri

- `Response` alanları nihai metrik ihtiyaçlarına göre güncellenmeli.
- `ExperimentConfig`, UI preference, vLLM endpoint, model role ve custom dataset alanlarını desteklemeli.
- `config.py`, bilinmeyen YAML alanlarını sessizce düşürmemeli veya explicit validation yapmalı.
- Model isimleri frontend/API/core arasında normalize edilmeli.
- Yeni model havuzunda resmi checkpoint adları ile repo alias'ları (`qwen3.5-397b-a17b`, `gemma4-4b` gibi) karıştırılmamalı.
- Prompt parser'ları benchmark bazlı daha sağlam hale getirilmeli.

## Evaluation and Analysis İşleri

- `compute_metrics()` çıktıları runner/MLflow hattına bağlanmalı.
- EATS, p50/p95, total_tokens ve cost metrikleri tek kaynak üzerinden loglanmalı.
- `energy.py` ve `cost.py`, deney sonucu üretimine entegre edilmeli.
- `analysis/energy_report.py` beklediği alanlarla reporter çıktısı uyumlu hale getirilmeli.
- `results/*.json` şeması netleştirilmeli ve README/agent context'te sabitlenmeli.

## Experiments İşleri

- `--config ... --dry_run` davranışı düzeltilmeli.
- `architecture: all` config üzerinden geldiğinde expansion yapılmalı veya config invalid sayılmalı.
- Prototip architecture config'leri gerçek constructor imzalarıyla eşleştirilmeli.
- PLAN'deki checkpoint/resume desteği uygulanmalı veya plandan çıkarılmalı.
- Web backend mock experiment service yerine gerçek runner entegrasyonu planlanmalı.

## Docker İşleri

- `.env.example` eklenmeli veya compose `.env` yokken anlamlı çalışmalı.
- API Dockerfile extra ismi pyproject ile uyumlu hale getirilmeli.
- Compose'a runner service eklenip eklenmeyeceği netleştirilmeli.
- API servisinde Ollama base URL compose network'e göre ayarlanmalı.
- MLflow CMD env expansion davranışı doğrulanmalı.

## Infrastructure İşleri

- Terraform root/backend yapısı netleştirilmeli.
- ECR repo URL/path üretimi user_data içinde düzeltilmeli.
- CPU/GPU runner rolleri ayrıştırılmalı.
- Secret isimleri ve user_data beklentileri eşleştirilmeli.
- MLflow endpoint stratejisi belirlenmeli: local instance, ayrı service veya managed endpoint.

## MLOps İşleri

- `MLflowTracker.log_sample()` field isimleri `Response` tipiyle uyumlu hale getirilmeli.
- Final metric logging computed metrics ile uyumlu hale getirilmeli.
- Concurrent run senaryolarında MLflow global state gözden geçirilmeli.
- Registry helper gerçek akışta kullanılacaksa runner/tracker ile bağlanmalı.

## Training / Fine-Tuning İşleri

- Fine-tuned adapter'ların inference sırasında nasıl yükleneceği core model provider tarafında tasarlanmalı.
- Adapter registry ile experiment config arasında bağlantı kurulmalı.
- Base SLM vs fine-tuned SLM vs LLM ablation config'leri eklenmeli.
- Training çıktıları MLflow artifact/model registry tarafına bağlanmalı.
- Custom stratified coding dataset hazırlandığında `training/data/processed/*` dosyaları üretilmeli.
- Human preference benchmark'ta fine-tuned model cevapları ayrı treatment olarak loglanmalı.

## Web İşleri

- LLM Arena UI veri modeli tasarlanmalı.
- Live chat preference akışı tasarlanmalı.
- İnsan tercih kayıtları benchmark/evaluation hattına bağlanmalı.
- Mock experiment service yerine gerçek experiment runner entegrasyonu yapılmalı.
- Benchmark/model/architecture isimleri backend ve frontend arasında normalize edilmeli.
