"""
Kullanıcının senaryosunu test et:
1. Görüntü yükle
2. Şifrele
3. Şifreli görüntüyü kaydet
4. Deşifrele
"""

import numpy as np
import cv2
from encryption import encrypt_image_from_array, decrypt_image

print('='*70)
print('KULLANICI SENARYOSU TESTİ')
print('='*70)

# 1. Görüntü yükle (kullanıcı bir dosya seçiyor)
print('\n[1] Görüntü yükleniyor...')
original = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
cv2.imwrite('test_user_original.png', original)
original_loaded = cv2.imread('test_user_original.png', cv2.IMREAD_GRAYSCALE)
print(f'    Orijinal: {original_loaded.shape}, min={original_loaded.min()}, max={original_loaded.max()}')

# 2. Şifrele (kullanıcı "Şifrele" butonuna basıyor)
print('\n[2] Şifreleme yapılıyor...')
key = [0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1]
encrypted = encrypt_image_from_array(original_loaded, key)
print(f'    Şifreli: {encrypted.shape}, min={encrypted.min()}, max={encrypted.max()}')

# 3. Şifreli görüntüyü kaydet (kullanıcı "Şifreli Görüntüyü Kaydet" yapıyor)
print('\n[3] Şifreli görüntü kaydediliyor...')
save_path = 'test_user_encrypted.png'
cv2.imwrite(save_path, encrypted)
print(f'    Kaydedildi: {save_path}')

# 4. Deşifrele (kullanıcı "Deşifrele" butonuna basıyor)
print('\n[4] Deşifreleme yapılıyor...')
# GUI'de self.encrypted_image kullanılıyor (bellekteki)
decrypted = decrypt_image(encrypted, key, original_loaded)
print(f'    Deşifreli: {decrypted.shape}, min={decrypted.min()}, max={decrypted.max()}')

# 5. Doğrulama
print('\n[5] DOĞRULAMA')
mse = np.mean((original_loaded - decrypted) ** 2)
print(f'    MSE: {mse}')

if mse == 0:
    print('    ✅ BAŞARILI - Deşifreleme mükemmel!')
else:
    print(f'    ❌ HATA - MSE: {mse}')
    
    # Detaylı analiz
    diff = np.abs(original_loaded.astype(int) - decrypted.astype(int))
    print(f'    Farklı piksel sayısı: {np.count_nonzero(diff)}')
    print(f'    Maksimum fark: {diff.max()}')
    print(f'    Ortalama fark: {diff.mean():.2f}')
    
    # İlk 10 farklı pikseli göster
    diff_indices = np.where(diff > 0)
    if len(diff_indices[0]) > 0:
        print('\n    İlk 10 farklı piksel:')
        for i in range(min(10, len(diff_indices[0]))):
            row, col = diff_indices[0][i], diff_indices[1][i]
            print(f'      [{row},{col}]: {original_loaded[row,col]} → {decrypted[row,col]} (fark: {diff[row,col]})')

print('\n' + '='*70)
