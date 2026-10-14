# 🎙️ AudioCleaner

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Faster-Whisper](https://img.shields.io/badge/whisper-faster--whisper-orange.svg)](https://github.com/SYSTRAN/faster-whisper)
[![FFmpeg](https://img.shields.io/badge/ffmpeg-anti--click%20cuts-green.svg)](https://ffmpeg.org/)

AudioCleaner, Türkçe ve çok dilli ses ve video kayıtlarındaki asalak sesleri (*"ııı"*, *"eee"*, *"şey"*, *"yani"*, *"ımm"*) ve rahatsız edici duraklamaları sıfır ek maliyetle ($0) tespit edip, 12-15ms sıfır-geçişli mikro cross-fade ile pürüzsüzce temizleyen hafif bir yapay zeka aracıdır.

---

## ⚡ Hızlı Başlangıç

```bash
# 1. Bağımlılığı yükleyin (FFmpeg sisteminizde kurulu olmalıdır)
pip install -r requirements.txt

# 2. Ses veya video dosyasını temizleyin
python clean_audio.py "kayit.mp3"

# 3. Yalnızca fonetik sesleri temizleyin (kelimeleri koruyun)
python clean_audio.py "video.mp4" --mode sounds_only

# 4. Kesim yapmadan tarama raporu alın
python clean_audio.py "roportaj.wav" --dry-run
```

---

## 📚 Dokümantasyon

| Belge | Açıklama |
| :--- | :--- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Modüler mimari, Whisper salise tespiti ve FFmpeg micro-fade tasarımı |
| [ROADMAP.md](ROADMAP.md) | Sürüm planları ve gelecek özellikler |
| [CHANGELOG.md](CHANGELOG.md) | SemVer sürüm geçmişi ve değişiklikler |
| [KNOWLEDGE.md](KNOWLEDGE.md) | Akustik gotchas, click-pop önleme ve Türkçe fonetik kuralları |
| [TASKS.md](TASKS.md) | Aktif görev takibi ve backlog |
| [SKILLS.md](SKILLS.md) | Proje çalışma kuralları, dokunulmaz sınırlar ve DoD |
| [LICENSE](LICENSE) | GNU General Public License v3.0 |
