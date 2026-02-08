"""
Gerçek Görüntü ile Kapsamlı Deşifreleme Testi
"""

import numpy as np
import cv2
from encryption import encrypt_image, decrypt_image

print("="*70)
print("KAPSAMLI DEŞİFRELEME TESTİ")
print("="*70)

# Test görüntüsü oluştur - Daha karmaşık pattern
print("\n[1] Test görüntüsü oluşturuluyor (256x256)...")
H, W = 256, 256
test_img = np.zeros((H, W), dtype=np.uint8)

# Karmaşık pattern: gradyan + sinüs dalgaları + rastgele gürültü
for i in range(H):
    for j in range(W):
        gradient = (i + j) % 256
        wave = int(50 * np.sin(i/10) + 50 * np.cos(j/10))
        noise = np.random.randint(-20, 20)
        test_img[i, j] = np.clip(gradient + wave + noise, 0, 255)

cv2.imwrite("test_complex_original.png", test_img)
print(f"   ✓ Orijinal kaydedildi: test_complex_original.png")
print(f"   Boyut: {test_img.shape}")
print(f"   Min: {test_img.min()}, Max: {test_img.max()}, Mean: {test_img.mean():.2f}")

# Anahtar
key = [0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1]

# Şifrele (dosya üzerinden)
print("\n[2] Şifreleme yapılıyor...")
encrypted = encrypt_image("test_complex_original.png", key)
cv2.imwrite("test_complex_encrypted.png", encrypted)
print(f"   ✓ Şifreli kaydedildi: test_complex_encrypted.png")
print(f"   Min: {encrypted.min()}, Max: {encrypted.max()}, Mean: {encrypted.mean():.2f}")

# Entropi hesapla
hist_orig = cv2.calcHist([test_img], [0], None, [256], [0, 256])
hist_enc = cv2.calcHist([encrypted], [0], None, [256], [0, 256])

hist_orig = hist_orig.ravel() / hist_orig.sum()
hist_enc = hist_enc.ravel() / hist_enc.sum()

entropy_orig = -np.sum(hist_orig[hist_orig > 0] * np.log2(hist_orig[hist_orig > 0]))
entropy_enc = -np.sum(hist_enc[hist_enc > 0] * np.log2(hist_enc[hist_enc > 0]))

print(f"   Entropi Orijinal: {entropy_orig:.4f} bit")
print(f"   Entropi Şifreli:  {entropy_enc:.4f} bit")

# Deşifrele
print("\n[3] Deşifreleme yapılıyor...")
decrypted = decrypt_image(encrypted, key, test_img)
cv2.imwrite("test_complex_decrypted.png", decrypted)
print(f"   ✓ Deşifreli kaydedildi: test_complex_decrypted.png")

# Detaylı karşılaştırma
print("\n[4] Detaylı Analiz:")
print("-"*70)

mse = np.mean((test_img - decrypted) ** 2)
print(f"MSE (Mean Squared Error):     {mse:.10f}")

psnr = float('inf') if mse == 0 else 10 * np.log10(255**2 / mse)
print(f"PSNR (Peak Signal-to-Noise):  {psnr:.2f} dB")

# Piksel piksel karşılaştırma
identical_pixels = np.sum(test_img == decrypted)
total_pixels = test_img.size
print(f"Özdeş piksel sayısı:          {identical_pixels} / {total_pixels}")
print(f"Özdeşlik oranı:               {(identical_pixels/total_pixels)*100:.4f}%")

if mse == 0:
    print("\n" + "="*70)
    print("✅ MÜKEMMEL! Deşifreleme %100 başarılı!")
    print("   Orijinal görüntü bit-bit geri kazanıldı!")
    print("="*70)
else:
    print("\n" + "="*70)
    print(f"❌ HATA! Deşifreleme tam değil!")
    print("="*70)
    
    # Hata analizi
    diff = np.abs(test_img.astype(int) - decrypted.astype(int))
    
    print(f"\nHata İstatistikleri:")
    print(f"  Maksimum fark:     {diff.max()}")
    print(f"  Ortalama fark:     {diff.mean():.4f}")
    print(f"  Standart sapma:    {diff.std():.4f}")
    print(f"  Farklı piksel:     {np.sum(diff > 0)}")
    
    # İlk 10 farklı pikseli göster
    wrong_pixels = np.where(diff > 0)
    if len(wrong_pixels[0]) > 0:
        print(f"\n  İlk 5 hatalı piksel:")
        for idx in range(min(5, len(wrong_pixels[0]))):
            i, j = wrong_pixels[0][idx], wrong_pixels[1][idx]
            print(f"    [{i},{j}]: {test_img[i,j]} → {decrypted[i,j]} (fark: {diff[i,j]})")
    
    # Fark haritası
    diff_map = (diff * 10).astype(np.uint8)
    cv2.imwrite("test_complex_diff.png", diff_map)
    print(f"\n  Fark haritası kaydedildi: test_complex_diff.png")

print("\n" + "="*70)
