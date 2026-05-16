# Agent Working Agreement

Bu repo üzerinde çalışan agent'lar aşağıdaki kuralları takip etmelidir.

## Başlangıç

- Önce `.agents/README.md` dosyasını oku.
- İş benchmark, architecture, metric veya experiment ile ilgiliyse ilgili `.agents/*` dosyasını da oku.
- Sonra gerçek kaynak kodu kontrol et. Bu dosyalar bağlam sağlar ama kodun yerine geçmez.

## Kavramsal Kurallar

- Bu repodaki `HumanEval` adını OpenAI HumanEval olarak yorumlama.
- `HumanEval` işleri insan tercih benchmark'ı olarak ele alınmalı.
- `custom_stratified.py` işleri easy/medium/hard kodlama dataset'i olarak ele alınmalı.
- `eats` bir benchmark değil, metriktir.
- Architecture katmanının görevi, aynı `Query` girdisine farklı stratejilerle cevap üretip ortak `Response` döndürmektir.
- Model isimleri geçerken önce repo alias'ını (`qwen3.5-4b`, `llama3.3-70b` gibi), gerektiğinde de buna karşılık gelen resmi checkpoint'i kullan.

## Kod Değişikliği Kuralları

- Mevcut pattern'i oku, sonra değişiklik yap.
- İlgisiz refactor yapma.
- Kullanıcının veya başka agent'ın değişikliklerini geri alma.
- Type contract değiştirirken runner, tests, docs ve ilgili architecture'ları birlikte düşün.
- Benchmark semantiğini değiştiren işlerde README/PLAN/DESIGN_DECISIONS ve `.agents` context'i de güncel tutulmalı.

## Doğrulama Komutları

Kapsama göre aşağıdaki komutları kullan:

```bash
python -m py_compile benchmarks/*.py
python -m py_compile experiments/*.py
python -m py_compile mlops/*.py
pytest tests/test_metrics.py -q
python -m experiments.run_experiment --architecture all --benchmark mmlu --n_samples 1 --dry_run
```

Terraform değişikliklerinde ilgili environment dizininde:

```bash
terraform init -backend=false
terraform validate
```

Docker değişikliklerinde:

```bash
docker compose -f docker/docker-compose.yml config
```

Not: Compose şu an `.env` yoksa hata verebilir. Bu durum bilinen gap'tir.

## Dokümantasyon Beklentisi

- Kullanıcı repo extraction sürecinde kısa, her noktaya değinen açıklamalar istiyor.
- Açıklamalarda "planlanan amaç" ile "şu an çalışan durum" ayrı tutulmalı.
- Eksikler açıkça söylenmeli ama gereksiz uzun listeye boğulmamalı.
