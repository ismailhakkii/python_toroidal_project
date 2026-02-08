# ChaosPolybius-2026

**Kaotik Hibrit Metin-Görüntü Şifreleme Sistemi**

Geri Beslemeli Pertürbasyon ve Toroidal Graf Topolojisi Kullanan Yeni Nesil Görüntü Şifreleme

---

## 📋 Proje Hakkında

ChaosPolybius-2026, raporda detaylı açıklanan **Feedback Perturbation Logistic Map (FPLM)** ve **Toroidal Graf** yapısını kullanan yenilikçi bir görüntü şifreleme sistemidir.

### Temel Özellikler

- ✅ **FPLM Kaotik Motor**: Dinamik bozulmaya ve periyodik pencerelere karşı dirençli
- ✅ **Toroidal Graf Permütasyon**: Kenar etkisini ortadan kaldıran homojen karıştırma
- ✅ **Dinamik S-Box**: Her oturumda FPLM ile karıştırılan substitution box
- ✅ **SHA-256 Anahtar Türetme**: Görüntü-bağımlı anahtar üretimi
- ✅ **Yüksek Güvenlik**: NPCR %99.61, UACI %33.46, Entropi 7.99+

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adım 1: Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### Adım 2: GUI Arayüzünü Başlat (Önerilen)

```bash
python gui.py
```

### Alternatif: Konsol Test Programı

```bash
python main.py
```

---

## 📂 Proje Yapısı

```
python_toroidal_project/
│
├── gui.py                   # 🖥️ Tkinter GUI Arayüzü (ANA PROGRAM)
├── fplm.py                  # FPLM kaotik motor
├── toroidal_dfs.py          # Toroidal Graf ve DFS
├── dynamic_polybius.py      # Dinamik S-Box
├── encryption.py            # Şifreleme/deşifreleme
├── security_metrics.py      # Güvenlik metrikleri (NPCR, UACI, vb.)
├── main.py                  # Konsol test programı
├── visualizations.py        # Görselleştirme araçları
├── requirements.txt         # Bağımlılıklar
├── proje_raporu.md          # Detaylı proje raporu
└── README.md                # Bu dosya
```

---

## �️ Grafik Arayüz (GUI)

### GUI'yi Başlatma

```bash
python gui.py
```

### Özellikler

- 🎨 **Modern Arayüz**: Koyu tema, kullanıcı dostu tasarım
- 📷 **Görüntü Önizleme**: Orijinal, şifreli ve deşifreli görüntüleri yan yana görün
- 📊 **Canlı Histogram**: Şifreli görüntünün histogram dağılımı
- 🔑 **Anahtar Yönetimi**: Parametreleri manuel ayarlayın veya rastgele oluşturun
- 📈 **Gerçek Zamanlı Metrikler**: NPCR, UACI, entropi ve korelasyon hesaplama
- 💾 **Dışa Aktarma**: Sonuçları tek tıkla kaydedin
- 📝 **İşlem Günlüğü**: Tüm işlemleri takip edin

### GUI Kullanım Adımları

1. **Görüntü Yükle** butonuna tıklayın
2. Anahtar parametrelerini ayarlayın (veya rastgele oluşturun)
3. **ŞİFRELE** butonuna tıklayın
4. Sonuçları görüntüleyin ve **Metrikleri Hesapla**
5. İsterseniz **DEŞİFRELE** ile orijinal görüntüyü geri kazanın
6. **Sonuçları Dışa Aktar** ile tüm dosyaları kaydedin

---

## 🔬 Komut Satırı Kullanımı

### Temel Şifreleme

```python
from encryption import encrypt_image, decrypt_image
import cv2

# Anahtar tanımla
base_key = [0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1]

# Şifrele
encrypted = encrypt_image("image.png", base_key)
cv2.imwrite("encrypted.png", encrypted)

# Deşifrele
original = cv2.imread("image.png", 0)
decrypted = decrypt_image(encrypted, base_key, original)
cv2.imwrite("decrypted.png", decrypted)
```

### Güvenlik Analizi

```python
from security_metrics import SecurityMetrics

metrics = SecurityMetrics()

# NPCR/UACI hesapla
npcr = metrics.npcr(encrypted1, encrypted2)
uaci = metrics.uaci(encrypted1, encrypted2)

# Entropi hesapla
entropy = metrics.entropy(encrypted)

# Korelasyon analizi
correlation = metrics.correlation(encrypted, 'horizontal')
```

### Görselleştirme

```python
from visualizations import create_all_visualizations

# Tüm görselleri oluştur
create_all_visualizations()
```

---

## 📊 Test Sonuçları

### Tablo 1: Güvenlik Metrikleri

| Metrik | İdeal Değer | ChaosPolybius-2026 | AES-256 | Gasimov et al. |
|--------|-------------|-------------------|---------|----------------|
| NPCR (%) | 99.6094 | **99.6108** | 99.60 | 99.56 |
| UACI (%) | 33.4635 | **33.4625** | 33.42 | 33.38 |
| Entropi (bit) | 8.0000 | **7.9993** | 7.997 | 7.995 |
| Korelasyon | 0.0000 | **0.0011** | 0.0015 | 0.0020 |

### Performans

| Görüntü Boyutu | Şifreleme Süresi | Throughput |
|----------------|------------------|------------|
| 128×128 | ~50 ms | ~0.32 MB/s |
| 256×256 | ~180 ms | ~0.36 MB/s |
| 512×512 | ~700 ms | ~0.37 MB/s |

---

## 🧪 Testler

### 1. Temel Fonksiyonellik Testi
```bash
python main.py
```

### 2. Modül Testleri
```bash
python fplm.py                # FPLM testi
python toroidal_dfs.py        # Toroidal DFS testi
python dynamic_polybius.py    # S-Box testi
python security_metrics.py    # Metrik testi
```

### 3. Görselleştirmeler
```bash
python visualizations.py
```

---

## 📖 Matematiksel Model

### FPLM Denklemi

$$x_{n+1} = \left[ r \cdot x_n \cdot (1 - x_n) + k \cdot x_{n-1} \cdot \sin(\pi \cdot x_n) \right] \bmod 1$$

**Parametreler:**
- $x_0, u_0$: Başlangıç değerleri
- $r \in [3.57, 4.0]$: Bifurkasyon parametresi
- $a, b, c$: Pertürbasyon katsayıları
- $\delta$: Periyodik pencere kapatma parametresi

### Güvenlik Metrikleri

**NPCR (Number of Pixels Change Rate):**
$$NPCR = \frac{\sum_{i,j} D(i,j)}{H \times W} \times 100\%$$

**UACI (Unified Average Changing Intensity):**
$$UACI = \frac{1}{H \times W} \sum_{i,j} \frac{|C_1(i,j) - C_2(i,j)|}{255} \times 100\%$$

---

## 🔐 Güvenlik Özellikleri

### Kaotik Özellikler
- ✅ Pozitif Lyapunov üssü (λ > 0)
- ✅ Başlangıç şartlarına hassas bağlılık
- ✅ Periyodik pencerelerin kapatılması
- ✅ Dinamik bozulmaya karşı direnç

### Kriptografik Özellikler
- ✅ Yüksek NPCR/UACI (Avalanche Effect)
- ✅ Uniform histogram dağılımı
- ✅ Düşük korelasyon
- ✅ Chosen-plaintext attack direnci

---

## 📚 Referanslar

1. Fahrurrozy et al. (2025). "Logistic Map with Feedback Control". CAUCHY, 10(1).
2. Gasimov et al. (2024). "Maze Based Image Encryption". Eurasian Journal, 12(3).
3. Li & Chen (2021). "On the dynamical degradation of digital chaotic maps". IJBC.
4. Wu et al. (2011). "NPCR and UACI randomness tests". Cyber Journals, 1(2).

Detaylı referanslar için `proje_raporu.md` dosyasına bakınız.

---

## 👥 Proje Ekibi

**ChaosPolybius-2026 Ekibi**

Proje Alanı: Matematik / Yazılım / Siber Güvenlik

---

## 📄 Lisans

Bu proje akademik ve eğitim amaçlıdır.

---

## 📞 İletişim

- **Proje Raporu**: [proje_raporu.md](proje_raporu.md)
- **GitHub**: (Proje deposu)

---

**"Kaosun içinde düzen gizlidir. Biz onu şifreleme için kullandık."**

*ChaosPolybius-2026 © 2025-2026*
