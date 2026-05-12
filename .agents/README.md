# Agent Context Index

Bu dizin, repo üzerinde çalışacak agent'ların aynı proje bağlamından başlaması için oluşturuldu. Yeni bir agent önce bu dosyayı, sonra ihtiyacına göre aşağıdaki dosyaları okumalıdır.

## Okuma Sırası

1. [project-context.md](project-context.md): Projenin neden var olduğu, kapsamı ve kritik terminoloji.
2. [repo-map.md](repo-map.md): Dizinlerin rolü, mevcut durumu ve birbirleriyle ilişkisi.
3. [known-gaps.md](known-gaps.md): Şu an bilinen eksikler, kırılgan noktalar ve yapılacak işler.
4. [working-agreement.md](working-agreement.md): Agent'ların repo içinde nasıl çalışacağına dair kurallar.
5. [handoff.md](handoff.md): Yeni agent'a verilebilecek kısa başlangıç prompt'u.

## Kısa Özet

Bu monorepo, tez kapsamında SLM/LLM tabanlı farklı cevap üretme mimarilerini aynı benchmark, metrik ve deney altyapısı üzerinden karşılaştırmak için var.

Karşılaştırılan şey tek başına model kalitesi değildir. Asıl karşılaştırma, aynı `Query` girdisine farklı mimari/orkestrasyon stratejilerinin nasıl cevap verdiği, ne kadar doğru/hızlı/ucuz olduğu ve insan tercihinde nasıl performans gösterdiğidir.

En kritik terminoloji düzeltmesi: bu repodaki `HumanEval`, OpenAI HumanEval kod üretimi benchmark'ı anlamına gelmez. Projeye özel insan tercih benchmark'ıdır.

