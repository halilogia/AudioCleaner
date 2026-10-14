# 📝 Değişiklik Günlüğü (Changelog)

Tüm önemli değişiklikler bu dosyada belgelenecektir.  
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), Sürümleme: [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-10-14

### Added
- Faster-Whisper int8 kelime seviyesi salise zaman damgalama motoru (`filler_detector.py`).
- Türkçe ve İngilizce fonetik asalak ses kütüphanesi (ııı, eee, şey, yani, falan, um, uh).
- Doğal nefes payı korumalı duraklama budama algoritması.
- FFmpeg 12ms sıfır-geçişli mikro-fade (`afade`) kurgu borusu (`audio_cutter.py`).
- Windows CLI sınırını aşan geçici script tabanlı filtreleme (`-filter_complex_script`).
- Hem ses hem video girişlerini destekleyen `clean_audio.py` komut satırı arayüzü.
- Birim testleri (`tests/test_cleaner.py`) ve 8 çekirdek dokümantasyon standardı.
