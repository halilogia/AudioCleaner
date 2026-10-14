# 🗺️ AudioCleaner Yol Haritası (Roadmap)

## 🚀 v1.0.0 (Mevcut Sürüm / MVP)
- [x] Faster-Whisper int8 tabanlı kelime düzeyi salise damgalama.
- [x] Türkçe fonetik asalak ses sözlüğü (`"ııı"`, `"eee"`, `"şey"`, `"yani"`, `"ımm"`).
- [x] Otomatik duraklama ve ölü zaman (dead air) budama.
- [x] 12-15ms sıfır-geçişli mikro cross-fade (pop/click önleyici).
- [x] Windows CLI limitini aşan `-filter_complex_script` FFmpeg borusu.
- [x] Hem ses (.mp3/.wav/.m4a) hem video (.mp4/.mov) desteği.
- [x] Dry-run analiz ve JSON raporlama.

## ⏳ v1.1.0 (Aktif Sprint)
- [ ] SRT/VTT altyazı dosyalarını otomatik zaman kaydırma ile senkron güncelleme.
- [ ] Kullanıcı tanımlı kara liste kelimeleri için regex genişletmesi.
- [ ] ClaudeVideoEditor kurgu hattına doğrudan ara yazılım (middleware) entegrasyonu.

## 🔭 v2.0.0 (Gelecek Vizyon)
- [ ] Streamlit veya Tauri tabanlı yerel görsel dalga formu (waveform) önizleme arayüzü.
- [ ] Canlı OBS kayıt sonrası otomatik tetikleyici kancası (post-record hook).
