# RTX6000 Model Switching

RTX6000 host shared çalışır. Aynı anda tek model açıktır.

## SSH

```bash
gcloud compute ssh dogukan-topcu-rtx6000-spot \
  --project=hubx-ml-playground \
  --zone=europe-west2-c
```

## Mevcut modeli kontrol et

```bash
sudo docker ps
sudo docker logs --tail 20 mid-llm
```

## Model değiştir

Örnek:

```bash
~/run-mid-llm.sh gemma4-31b
sudo docker logs -f mid-llm
```

## Validation

```bash
curl -fsS http://localhost:8000/v1/models | jq .
```

`/v1/models` yeni modeli gösteriyorsa switch tamamdır.

## Auto-switch

Backend auto-switch destekler. `THESIS_RTX6000_AUTOSWITCH_ENABLED=true`
olduğunda experiment başlamadan önce seçilen `llm` için host otomatik değiştirilir.
