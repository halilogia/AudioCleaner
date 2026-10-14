# 📜 AudioCleaner Ajan Anayasası (AGENTS.md)

Bu belge, AudioCleaner projesinde çalışan tüm yapay zeka ajanlarının (Antigravity, Claude Code, Codex) uymak zorunda olduğu mutlak kuralları tanımlar.

---

## 1. Temel Görev & Vibe
- **Amaç:** Ses ve video konuşmalarındaki asalak sesleri ve gereksiz duraklamaları sıfır ek kütüphane şişkinliğiyle ($0 harici maliyet) temizlemek.
- **Hissiyat:** Cerrahi, stüdyo kalitesinde, pürüzsüz ve ultra hızlı.

---

## 2. Dokunulmaz Sınırlar & Yasaklar

1. **Sert Kesim Yasağı:** Kesim noktalarında `afade` kullanılmadan çıplak birleştirme (`concat`) yapılması KESİNLİKLE YASAKTIR.
2. **Kelimeleri Yutma Yasağı:** Bitişik veya anlamlı Türkçe kelimeleri (`ışık`, `iki` vb.) asalak ses sanıp budayacak agresif substring eşleşmeleri yapılamaz; sadece Whisper'ın tam sözcük tokenleri ayrıştırılır.
3. **Paha / Şişkinlik Yasağı:** Projeye harici bulut API'ları (OpenAI paid API vb.) veya ağır GUI kütüphaneleri eklenemez.
4. **Cerrahi Düzenleme Kuralı:** Dosyalarda değişiklik yapılırken tüm dosya baştan yazılmaz; yalnızca ilgili fonksiyon ve satırlar hedeflenir.

---

## 3. Tamamlanma Kriteri (Definition of Done)
Herhangi bir PR veya değişiklik öncesinde şu komut hatasız geçmelidir:
```bash
python -m unittest tests/test_cleaner.py
```
Testler geçmeden hiçbir commit oluşturulamaz veya push edilemez.
