"""
Hızlı Deşifreleme Test Scripti
"""

import numpy as np
import cv2
from encryption import encrypt_image_from_array, decrypt_image

print("="*60)
print("Deşifreleme Testi")
print("="*60)

# Test görüntüsü oluştur (128x128)
print("\n1. Test görüntüsü oluşturuluyor...")
test_img = np.random.randint(0, 256, (128, 128), dtype=np.uint8)

# Gradyan pattern ekle (görsel kontrol için)
for i in range(128):
    for j in range(128):
        test_img[i, j] = (i + j) % 256

cv2.imwrite("test_original_decrypt.png", test_img)
print(f"   Orijinal kaydedildi: test_original_decrypt.png")

# Anahtar
key = [0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1]

# Şifrele
print("\n2. Şifreleme yapılıyor...")
encrypted = encrypt_image_from_array(test_img, key)
cv2.imwrite("test_encrypted_decrypt.png", encrypted)
print(f"   Şifreli kaydedildi: test_encrypted_decrypt.png")

# Deşifrele
print("\n3. Deşifreleme yapılıyor...")
decrypted = decrypt_image(encrypted, key, test_img)
cv2.imwrite("test_decrypted_decrypt.png", decrypted)
print(f"   Deşifreli kaydedildi: test_decrypted_decrypt.png")

# Karşılaştır
mse = np.mean((test_img - decrypted) ** 2)
print(f"\n4. Sonuç:")
print(f"   MSE (Mean Squared Error): {mse}")

if mse == 0:
    print("   ✅ BAŞARILI - Orijinal görüntü tamamen geri kazanıldı!")
else:
    print(f"   ❌ HATA - Deşifreleme başarısız! MSE: {mse}")
    
    # Fark analizi
    diff = np.abs(test_img.astype(int) - decrypted.astype(int))
    max_diff = np.max(diff)
    mean_diff = np.mean(diff)
    
    print(f"\n   Fark İstatistikleri:")
    print(f"   - Maksimum fark: {max_diff}")
    print(f"   - Ortalama fark: {mean_diff:.2f}")
    print(f"   - Farklı piksel sayısı: {np.sum(diff > 0)} / {test_img.size}")
    
    # Fark haritası kaydet
    cv2.imwrite("test_diff_map.png", diff.astype(np.uint8) * 10)
    print(f"   - Fark haritası kaydedildi: test_diff_map.png")

print("\n" + "="*60)
