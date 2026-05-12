# Training Data

Bu dizin training dataset'leri için yer tutucudur. Büyük dataset dosyaları git'e eklenmemelidir.

Önerilen yerleşim:

```text
training/data/raw/
training/data/processed/
```

Raw dosya örneği:

```json
{"id": "coding-easy-001", "prompt": "Return the sum of two integers.", "response": "def add(a, b):\n    return a + b", "difficulty": "easy", "topic": "functions"}
```

Processed dosyalar `python -m training.datasets prepare-sft ...` ile üretilmelidir.

