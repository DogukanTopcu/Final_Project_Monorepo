# Repository Agent Instructions

Bu repoda çalışmaya başlamadan önce `.agents/README.md` dosyasını oku.

Kritik notlar:

- `HumanEval`, OpenAI HumanEval değildir; UI destekli insan tercih benchmark'ıdır.
- `custom_stratified.py`, easy/medium/hard kodlama problemleri dataset'i olarak ele alınmalıdır.
- `eats`, benchmark değil metriktir.
- Architecture katmanı aynı `Query` girdisine farklı stratejilerle cevap üretip ortak `Response` döndürmelidir.
- Detaylı proje bağlamı, repo haritası, bilinen boşluklar ve çalışma kuralları `.agents/` altındadır.

