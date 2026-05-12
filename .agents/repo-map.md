# Repo Map

Bu dosya repo dizinlerinin ne için var olduğunu ve mevcut durumda ne kadar işlevsel olduklarını özetler.

## `analysis/`

Amaç: Deney çalıştıktan sonra `results/*.json` çıktıları üzerinde analiz yapmak.

Mevcut durum:

- `statistical_analysis.py`, `evaluation.statistics` fonksiyonlarını kullanır.
- `pareto_analysis.py`, accuracy/latency/cost gibi metriklerle Pareto grafikleri hedefler.
- `energy_report.py`, enerji/karbon raporu üretmeyi hedefler.

Bilinen durum: Henüz sonuç üretim hattına tam bağlı değildir. `energy_report.py` bazı alanları bekler (`energy_kwh`, `co2_g`, `tokens_per_kwh`) ama reporter/response tarafı bunları düzenli üretmez.

## `architectures/`

Amaç: Aynı `Query` girdisine farklı model/orkestrasyon stratejileriyle cevap üretmek ve ortak `Response` döndürmek.

Aktif/çalışır görünenler:

- `routing`
- `multi_agent`
- `ensemble`

Prototip veya runner ile uyumsuz görünenler:

- `monolithic`
- `multi_agent_crew`
- `speculative_decoding`

Bilinen durum:

- Runner tüm architecture'lara `slm`, `llm`, `task_type` gibi parametreler geçiyor; bazı sınıflar bu imzayı kabul etmiyor.
- Bazı vLLM sınıfları `Response(total_tokens=...)` döndürmeye çalışıyor ama `Response` tipinde bu alan yok.
- `multi_agent_crew.py` CrewAI/LangGraph hedefinden bahsediyor ama şu an heuristic router + HTTP çağrısı seviyesinde.
- `ensemble` dokümantasyonda paralelleştirilebilir görünürken mevcut akış daha çok sıralı çalışır.

## `benchmarks/`

Amaç: Deneylerde kullanılacak dataset ve benchmark adaptörlerini sağlamak.

Registry'de aktif görünenler:

- `mmlu`
- `arc`
- `hellaswag`
- `gsm8k`
- `truthfulqa`

Plan/prototip olanlar:

- `humaneval.py`: Proje özelinde insan tercih benchmark'ı olarak planlanmıştır.
- `custom_stratified.py`: Easy/medium/hard kodlama benchmark dataset'i olarak planlanmıştır.

Bilinen durum:

- `humaneval` ve `custom_stratified` registry'ye bağlı değildir.
- İki dosyada da eski/prototip kod kalıntıları vardır ve doğrudan çalıştırıldığında `Benchmark`/`BaseBenchmark` uyumsuzlukları çıkabilir.
- Web/API tarafındaki bazı benchmark listelerinde `eats` benchmark gibi geçer; aslında metrik ismidir.

## `core/`

Amaç: Repo genelinde paylaşılan tipler, model provider'ları, prompt yardımcıları ve config yükleme.

Ana dosyalar:

- `types.py`: `Query`, `Response`, `ExperimentConfig`, `SampleResult`, `ExperimentResult`
- `models.py`: `ModelProvider`, Ollama/OpenAI/Together wrapper'ları, `get_model`
- `prompt.py`: MCQ/open prompt builder ve parser
- `config.py`: YAML config load/save

Bilinen durum:

- `Response`, bazı planlanan metrik alanlarını henüz taşımaz.
- `ExperimentConfig`, vLLM, HumanEval UI ve custom coding ihtiyaçlarına göre dar kalabilir.
- `config.py`, bilinmeyen YAML alanlarını düşürebilir.
- Frontend/model isimleri ile core model isimleri arasında uyuşmazlıklar olabilir.

## `docker/`

Amaç: API, runner, MLflow, frontend ve Ollama servislerini container ortamında ayağa kaldırmak.

Ana dosyalar:

- `Dockerfile.api`
- `Dockerfile.runner`
- `Dockerfile.mlflow`
- `docker-compose.yml`

Bilinen durum:

- `docker compose -f docker/docker-compose.yml config`, `.env` olmadığı için başarısız oldu.
- API Dockerfile `.[api]` extra'sını kullanıyor; pyproject extra isimleriyle doğrulanmalı.
- Compose içinde runner image var ama runner service yok.
- API için Ollama base URL compose ağına göre ayarlanmamış olabilir.
- MLflow artifact root env expansion exec-form CMD içinde riskli olabilir.

## `evaluation/`

Amaç: Metrik hesaplama, istatistik ve sonuç raporlama.

Ana dosyalar:

- `metrics.py`
- `reporter.py`
- `statistics.py`
- `energy.py`
- `cost.py`

Mevcut durum:

- `pytest tests/test_metrics.py -q` geçti.
- `metrics.py` accuracy, latency, token ve EATS gibi hesapları içerir.
- `statistics.py`, `analysis/` tarafından kullanılır.

Bilinen durum:

- Runner MLflow'a çoğunlukla `result.to_metrics()` logluyor; `compute_metrics()` ile üretilen EATS/p50/p95 gibi değerler tam bağlanmamış olabilir.
- `energy.py` ve `cost.py` konsept olarak var ama ana deney hattına güçlü bağlı değildir.

## `experiments/`

Amaç: Deneyleri config/CLI üzerinden çalıştırmak.

Ana dosyalar:

- `runner.py`
- `run_experiment.py`
- `pilot_study.py`
- `configs/*.yaml`

Mevcut durum:

- `python -m py_compile experiments/*.py` geçti.
- `python -m experiments.run_experiment --architecture all --benchmark mmlu --n_samples 1 --dry_run` üç config doğruladı.

Bilinen durum:

- `--config ... --dry_run`, config override'larını tam uygulamadan benchmark yüklemeye çalışabilir.
- `architecture: all` config'ten gelirse sorun çıkarabilir.
- Bazı setup config'leri architecture constructor imzalarıyla uyumsuz.
- PLAN'de geçen checkpoint/resume henüz uygulanmış görünmüyor.
- Web backend şu an mock experiment service kullanıyor; gerçek runner'a bağlı değil.

## `infrastructure/`

Amaç: Bulut altyapısı, vLLM servisleri ve Terraform modülleri.

Ana parçalar:

- `vllm/docker-compose.yml`
- `vllm/serve_model.sh`
- `terraform/modules/*`
- `terraform/environments/dev`
- `terraform/environments/prod`

Mevcut durum:

- `terraform init -backend=false` ve `terraform validate` dev ortamında başarılı oldu.
- Sadece deprecation warning'leri görüldü.

Bilinen durum:

- Root `versions.tf` backend/provider ayarları environment dizinleriyle aynı Terraform root'u olmayabilir.
- EC2 user_data içinde ECR repo URL path'i iki kez ekleniyor olabilir.
- CPU instance runner çalıştırıyor gibi görünüyor; niyet GPU runner ise ayrıştırılmalı.
- Secret isimleriyle user_data beklentileri uyumlu olmayabilir.
- MLflow URI localhost olarak kalmış; instance içinde MLflow server varsayımı net değil.

## `mlops/`

Amaç: MLflow tracking, callback ve model registry yardımcıları.

Ana dosyalar:

- `tracking.py`
- `callbacks.py`
- `registry.py`

Mevcut durum:

- `python -m py_compile mlops/*.py` geçti.

Bilinen durum:

- `log_sample()` bazı eski field isimlerini kontrol ediyor olabilir (`latency`, `cost`) ama tipte `latency_ms`, `cost_usd` var.
- Final metric logging computed metrics yerine result metrics'e dayanıyor olabilir.
- MLflow global run state concurrency açısından dikkat ister.
- Web backend tarafında mock servis var; gerçek runner entegrasyonu ayrı iş.

## `training/`

Amaç: Fine-tune edilmiş SLM deneylerini ana orchestration benchmark hattından ayrı bir ablation ekseni olarak yönetmek.

Ana dosyalar:

- `README.md`
- `config.py`
- `datasets.py`
- `train_lora.py`
- `registry.py`
- `configs/qlora_coding_pilot.yaml`
- `configs/qlora_domain_pilot.yaml`

Mevcut durum:

- LoRA/QLoRA SFT için opsiyonel training paketi oluşturuldu.
- Dataset hazırlama, train/validation/test split, adapter registry ve örnek pilot config'ler var.
- Ağır bağımlılıklar `pip install -e ".[training]"` ile opsiyonel kurulacak şekilde ayrıldı.

Bilinen durum:

- Training hattı bilinçli olarak ana experiment runner'a doğrudan bağlanmadı.
- Fine-tuned adapter inference desteği core model provider ve architecture config tarafında ayrıca entegre edilmeli.
- Fine-tune sonuçları ana sonuçlarla karıştırılmadan ablation olarak raporlanmalı.

## `web/`

Amaç: Kullanıcı arayüzü ve API üzerinden deney yönetimi, sonuç gösterimi ve insan tercih değerlendirmesi.

Beklenen rol:

- LLM Arena arayüzü.
- Live chat preference arayüzü.
- Deney başlatma/izleme ekranları.

Bilinen durum: Bu repo extraction sırasında web detayına henüz ayrı ayrı inilmedi. Mevcut notlarda web backend'in mock experiment service kullandığı ve gerçek runner entegrasyonunun yapılmadığı belirtilmiştir.
