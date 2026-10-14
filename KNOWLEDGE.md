# 🧠 AudioCleaner Mühendislik Hafızası (Knowledge & Gotchas)

Bu belge, ses mühendisliği, Türkçe fonetik ve FFmpeg kurgu süreçlerinde karşılaşılan dersleri ve mimari kararları belgeler.

---

## 1. Akustik Gotchas ve Çözümleri

### Gotcha 1: Ham Kesimlerdeki Çıtlama (Pop/Click Artifacts)
- **Problem:** Ses dalgasının sıfır olmayan bir genlikte (non-zero crossing) aniden kesilmesi, hoparlörde veya kulaklıkta patlama/tıklama sesine neden olur.
- **Çözüm:** Kesilen her segmentin başına 12ms `afade=t=in:curve=tri`, sonuna 12ms `afade=t=out:curve=tri` uygulanır. İki parça birleştiğinde genlik sıfırdan yükselip sıfıra iner ve çıtlama tamamen yok edilir.

### Gotcha 2: Canlı Mikrofonda Kesim Yapmanın Tehlikesi
- **Problem:** Canlı yayında veya kayıt anında asalak sesleri susturmaya çalışmak mikrofon gecikmesine ve *"Işık"*, *"Irmak"*, *"İki"* gibi normal Türkçe kelimelerin başındaki seslerin yutulmasına yol açar.
- **Çözüm:** Kayıt ham alınır; temizleme işlemi kayıt sonrasında (post-processing) Faster-Whisper kelime bağlamı incelenerek yapılır.

### Gotcha 3: Windows Komut Satırı Karakter Sınırı (8192 Karakter)
- **Problem:** Uzun videolarda 50'den fazla kesim yapıldığında `-filter_complex "[0:a]atrim=...[a0];..."` dizesi Windows komut satırı sınırını aşarak `The command line is too long` hatası verir.
- **Çözüm:** Tüm filtre zinciri diskte geçici bir `.txt` dosyasına yazılır ve FFmpeg'e `-filter_complex_script <dosya>` olarak verilir.

### Gotcha 4: Türkçe Büyük "I" ve "İ" Harf Dönüşümü
- **Problem:** Standart Python `.lower()` fonksiyonu Türkçedeki büyük `I` harfini `i` olarak dönüştürebilir ve `ııı` sözcükleri eşleşmeyebilir.
- **Çözüm:** Metin temizliğinde `.replace("I", "ı").replace("İ", "i").lower()` sıralı dönüşümü zorunlu tutulur.
