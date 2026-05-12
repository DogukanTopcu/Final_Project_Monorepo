# Training

Bu dizin, fine-tune edilmiş küçük dil modeli deneylerini ana orchestration benchmark hattından ayrı tutmak için var.

Amaç, ana deneyi kirletmeden şu ablation sorusunu test etmektir:

> Domain/task özelinde fine-tune edilmiş bir SLM, doğru orchestration stratejisiyle büyük LLM'e göre daha iyi kalite/maliyet/latency/enerji dengesi sağlayabilir mi?

## Neden Ayrı?

Fine-tuning, modelin kendisini değiştirir. Ana deneyde amaç architecture etkisini ölçmek olduğu için base modeller sabit kalmalıdır. Fine-tuned modeller bu yüzden ayrı bir ablation ekseni olarak ele alınır.

## Önerilen Deney Matrisi

1. Base SLM
2. Fine-tuned SLM
3. LLM
4. Base SLM orchestration
5. Fine-tuned SLM orchestration
6. Fine-tuned SLM orchestration vs LLM

## Dizin Yapısı

- `config.py`: Training config şeması.
- `datasets.py`: JSONL dataset hazırlama, normalize etme ve split üretme CLI'ı.
- `train_lora.py`: LoRA/QLoRA SFT training CLI'ı.
- `registry.py`: Eğitilmiş adapter kayıt dosyasını yönetir.
- `configs/`: Pilot training config'leri.
- `data/`: Raw/processed training data yerleşimi.
- `adapters/`: Adapter registry ve yerel adapter çıktıları.

## Dataset Formatı

Tercih edilen SFT JSONL formatı:

```json
{"id": "coding-easy-001", "prompt": "Write a function...", "response": "def solve(...): ...", "difficulty": "easy", "topic": "arrays"}
```

Alternatif olarak doğrudan `text` alanı verilebilir:

```json
{"id": "domain-001", "text": "<|user|>\n...\n<|assistant|>\n..."}
```

Chat formatı da desteklenir:

```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

## Dataset Hazırlama

```bash
python -m training.datasets prepare-sft \
  --input training/data/raw/coding_pilot.jsonl \
  --output-dir training/data/processed/coding_pilot \
  --system-prompt "You are a concise coding assistant."
```

Bu komut şu dosyaları üretir:

- `training/data/processed/coding_pilot/train.jsonl`
- `training/data/processed/coding_pilot/validation.jsonl`
- `training/data/processed/coding_pilot/test.jsonl`

## Training

Önce opsiyonel training bağımlılıklarını kur:

```bash
pip install -e ".[training]"
```

Sonra pilot training'i çalıştır:

```bash
python -m training.train_lora --config training/configs/qlora_coding_pilot.yaml
```

Training tamamlanınca adapter bilgisi `training/adapters/registry.json` içine yazılır.

## Adapter Registry

Kayıtları listele:

```bash
python -m training.registry list
```

Manuel adapter kaydet:

```bash
python -m training.registry register \
  --name qlora-coding-pilot-phi3-mini \
  --base-model microsoft/Phi-3-mini-4k-instruct \
  --adapter-path training/adapters/qlora-coding-pilot-phi3-mini \
  --domain coding
```

## Değerlendirme Protokolü

Fine-tune sonucu ana benchmark ile karıştırılmamalıdır. Raporlama ayrı ablation olarak yapılmalıdır:

- Base model aynı benchmark'ta ölçülür.
- Fine-tuned adapter aynı benchmark'ta ölçülür.
- Aynı architecture, base ve fine-tuned SLM ile tekrar çalıştırılır.
- Sonuçlar accuracy, latency, cost, token, EATS ve insan tercihi ile karşılaştırılır.

