"""
ChaosPolybius-2026 Encryption System
Tam Şifreleme/Deşifreleme Modülü

Bu modül tüm bileşenleri bir araya getirir:
1. SHA-256 Anahtar Türetme
2. FPLM Kaotik Motor
3. Toroidal Permütasyon
4. Dinamik S-Box Difüzyon
"""

import cv2
import hashlib
import numpy as np
from fplm import FPLM
from toroidal_dfs import ToroidalDFS
from dynamic_polybius import DynamicPolybius

# Numba hızlandırma (opsiyonel - yoksa normal Python çalışır)
try:
    from fast_numba import (
        fast_permutation_apply,
        fast_inverse_permutation_apply,
        fast_xor_diffusion,
        fast_inverse_xor_diffusion,
        fast_sbox_substitute,
        fast_sbox_inverse
    )
    USE_NUMBA = True
    print("✅ Numba hızlandırma aktif!")
except ImportError:
    USE_NUMBA = False
    print("⚠️  Numba bulunamadı - normal hız modunda çalışıyor")


def sha256_key_derivation(image, base_key):
    """
    Base key'den deterministik anahtar türet
    
    NOT: Önceki sürümde görüntü hash'i kullanılıyordu ama bu deşifreleme 
    için orijinal görüntüyü gerektiriyordu (yanlış tasarım).
    Şimdi sadece base_key'den türetiliyor.
    
    Args:
    image : numpy array (görüntü) - kullanılmıyor, geriye uyumluluk için
    base_key : list [x0, u0, r, a, b, c, delta]
    
    Returns:
    list: Dinamik anahtar
    """
    # Base key'den deterministik hash üret
    key_str = ','.join(map(str, base_key))
    hash_digest = hashlib.sha256(key_str.encode()).hexdigest()
    
    # Hash'ten 7 sayı türet
    hash_values = []
    for i in range(0, 56, 8):
        hex_chunk = hash_digest[i:i+8]
        value = int(hex_chunk, 16) / 0xFFFFFFFF  # [0, 1] normalize
        hash_values.append(value)
    
    # Base key ile karıştır
    dynamic_key = list(base_key)
    dynamic_key[0] = (dynamic_key[0] + hash_values[0]) % 1.0  # x0
    dynamic_key[1] = (dynamic_key[1] + hash_values[1]) % 1.0  # u0
    dynamic_key[2] = dynamic_key[2] + (hash_values[2] * 0.1)  # r (küçük değişim)
    
    # Parametreleri sınırla
    dynamic_key[2] = max(3.57, min(4.0, dynamic_key[2]))
    
    return dynamic_key


def encrypt_image(image_path, base_key):
    """
    Görüntüyü şifrele
    
    Adımlar:
    1. Görüntüyü yükle
    2. SHA-256 ile dinamik anahtar türet
    3. Toroidal DFS ile permütasyon yap
    4. Dinamik S-Box ile substitution yap
    5. XOR zincirleme ile difüzyon yap
    
    Args:
    image_path : str - Görüntü yolu
    base_key : list [x0, u0, r, a, b, c, delta]
    
    Returns:
    numpy.ndarray: Şifreli görüntü
    """
    # 1. Görüntüyü yükle (gri seviye)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Görüntü bulunamadı: {image_path}")
    
    H, W = img.shape
    
    print(f"Görüntü yüklendi: {H}x{W}")
    
    # 2. Dinamik anahtar türet
    dynamic_key = sha256_key_derivation(img, base_key)
    print(f"Dinamik anahtar türetildi")
    
    # 3. FPLM başlat - Her işlem için AYRI state'e sahip kopyalar
    fplm_perm = FPLM(*dynamic_key)
    fplm_sbox = FPLM(*dynamic_key)  
    fplm_diff = FPLM(*dynamic_key)
    
    # 4. Permütasyon (Toroidal DFS)
    print(f"Permütasyon yapılıyor...")
    dfs = ToroidalDFS(H, W, fplm_perm)
    path = dfs.generate_path()
    
    flat_img = img.flatten()
    
    if USE_NUMBA:
        # Numba ile hızlı permütasyon
        path_flat_indices = np.array([r * W + c for r, c in path], dtype=np.int32)
        permuted_flat = fast_permutation_apply(flat_img, path_flat_indices)
    else:
        # Normal Python döngüsü
        permuted_flat = np.zeros_like(flat_img)
        for i, (r, c) in enumerate(path):
            orig_idx = r * W + c
            permuted_flat[i] = flat_img[orig_idx]
    
    print(f"Permütasyon tamamlandı {'(Numba hızlı mod)' if USE_NUMBA else ''}")
    
    # 5. S-Box Substitution
    print(f"S-Box substitution yapılıyor...")
    sbox = DynamicPolybius(fplm_sbox)
    
    if USE_NUMBA:
        substituted_flat = fast_sbox_substitute(permuted_flat, sbox.sbox)
    else:
        substituted_flat = sbox.substitute(permuted_flat)
    
    # 6. XOR Difüzyon (Zincirleme)
    print(f"XOR difüzyonu yapılıyor...")
    
    # FPLM'den anahtar akışı üret
    key_stream = fplm_diff.get_key_stream(H * W)
    
    if USE_NUMBA:
        encrypted_flat = fast_xor_diffusion(substituted_flat, key_stream)
    else:
        encrypted_flat = np.zeros(H * W, dtype=np.uint8)
        prev = 0
        
        for i in range(H * W):
            # Zincirleme XOR: C[i] = P[i] XOR K[i] XOR C[i-1]
            encrypted_flat[i] = substituted_flat[i] ^ key_stream[i] ^ prev
            prev = encrypted_flat[i]
    
    encrypted_img = encrypted_flat.reshape(H, W)
    
    print(f"Şifreleme tamamlandı")
    
    return encrypted_img


def decrypt_image(encrypted_img, base_key, original_img_for_hash):
    """
    Şifreli görüntüyü deşifrele
    
    Şifreleme adımlarını tersten uygular.
    
    Args:
    encrypted_img : numpy.ndarray - Şifreli görüntü
    base_key : list - Şifreleme anahtarı
    original_img_for_hash : numpy.ndarray - SHA-256 için orijinal görüntü
    
    Returns:
    numpy.ndarray: Deşifre edilmiş görüntü
    """
    H, W = encrypted_img.shape
    
    print(f"Deşifreleme başlıyor: {H}x{W}")
    
    # 1. Aynı dinamik anahtarı üret
    dynamic_key = sha256_key_derivation(original_img_for_hash, base_key)
    
    # 2. FPLM'leri başlat (şifreleme ile AYNI SIRADA ve AYRI state'ler)
    fplm_perm = FPLM(*dynamic_key)
    fplm_sbox = FPLM(*dynamic_key)  
    fplm_diff = FPLM(*dynamic_key)
    
    # 3. Toroidal DFS yolunu oluştur (şifreleme ile aynı)
    print(f"DFS yolu oluşturuluyor...")
    dfs = ToroidalDFS(H, W, fplm_perm)
    path = dfs.generate_path()
    
    # 4. S-Box oluştur (şifreleme ile aynı sırada)
    sbox = DynamicPolybius(fplm_sbox)
    
    # 5. XOR difüzyonunu ters çöz
    print(f"XOR difüzyonu çözülüyor...")
    key_stream = fplm_diff.get_key_stream(H * W)
    
    flat_encrypted = encrypted_img.flatten()
    
    if USE_NUMBA:
        substituted_flat = fast_inverse_xor_diffusion(flat_encrypted, key_stream)
    else:
        substituted_flat = np.zeros_like(flat_encrypted)
        prev = 0
        for i in range(H * W):
            # Ters zincirleme XOR: P[i] = C[i] XOR K[i] XOR C[i-1]
            substituted_flat[i] = flat_encrypted[i] ^ key_stream[i] ^ prev
            prev = flat_encrypted[i]
    
    # 6. S-Box'ı ters uygula
    print(f"S-Box ters substitution yapılıyor...")
    
    if USE_NUMBA:
        permuted_flat = fast_sbox_inverse(substituted_flat, sbox.inverse_sbox)
    else:
        permuted_flat = sbox.inverse_substitute(substituted_flat)
    
    # 7. Permütasyonu ters çöz
    print(f"Permütasyon tersine çevriliyor...")
    
    if USE_NUMBA:
        path_flat_indices = np.array([r * W + c for r, c in path], dtype=np.int32)
        decrypted_flat = fast_inverse_permutation_apply(permuted_flat, path_flat_indices)
    else:
        decrypted_flat = np.zeros_like(permuted_flat)
        for i, (r, c) in enumerate(path):
            orig_idx = r * W + c
            decrypted_flat[orig_idx] = permuted_flat[i]
    
    decrypted_img = decrypted_flat.reshape(H, W)
    
    print(f"Deşifreleme tamamlandı")
    
    return decrypted_img


def encrypt_image_from_array(img_array, base_key):
    """
    Numpy array'den direkt şifreleme yap
    (Test amaçlı - dosya kaydetmeye gerek yok)
    
    Args:
    img_array : numpy.ndarray - Görüntü array'i
    base_key : list - Anahtar
    
    Returns:
    numpy.ndarray: Şifreli görüntü
    """
    H, W = img_array.shape
    
    # Dinamik anahtar türet
    dynamic_key = sha256_key_derivation(img_array, base_key)
    
    # FPLM'leri başlat - Her işlem için AYRI state'e sahip kopyalar (şifreleme ile AYNI SIRA)
    fplm_perm = FPLM(*dynamic_key)
    fplm_sbox = FPLM(*dynamic_key)
    fplm_diff = FPLM(*dynamic_key)
    
    # Permütasyon
    dfs = ToroidalDFS(H, W, fplm_perm)
    path = dfs.generate_path()
    
    flat_img = img_array.flatten()
    
    if USE_NUMBA:
        path_flat_indices = np.array([r * W + c for r, c in path], dtype=np.int32)
        permuted_flat = fast_permutation_apply(flat_img, path_flat_indices)
    else:
        permuted_flat = np.zeros_like(flat_img)
        for i, (r, c) in enumerate(path):
            orig_idx = r * W + c
            permuted_flat[i] = flat_img[orig_idx]
    
    # S-Box (şifreleme ile aynı sırada)
    sbox = DynamicPolybius(fplm_sbox)
    
    if USE_NUMBA:
        substituted_flat = fast_sbox_substitute(permuted_flat, sbox.sbox)
    else:
        substituted_flat = sbox.substitute(permuted_flat)
    
    # XOR
    key_stream = fplm_diff.get_key_stream(H * W)
    
    if USE_NUMBA:
        encrypted_flat = fast_xor_diffusion(substituted_flat, key_stream)
    else:
        encrypted_flat = np.zeros(H * W, dtype=np.uint8)
        prev = 0
        
        for i in range(H * W):
            encrypted_flat[i] = substituted_flat[i] ^ key_stream[i] ^ prev
            prev = encrypted_flat[i]
    
    return encrypted_flat.reshape(H, W)


if __name__ == "__main__":
    # Test kodu
    print("="*60)
    print("ChaosPolybius-2026 Encryption System Test")
    print("="*60)
    
    # Test parametreleri
    base_key = [0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1]
    
    # Rastgele test görüntüsü oluştur (gerçek görüntü yerine)
    print("\nTest görüntüsü oluşturuluyor (128x128)...")
    test_img = np.random.randint(0, 256, (128, 128), dtype=np.uint8)
    cv2.imwrite("test_original.png", test_img)
    
    # Şifrele
    print("\nŞifreleme başlıyor...")
    encrypted = encrypt_image("test_original.png", base_key)
    cv2.imwrite("test_encrypted.png", encrypted)
    print(f"Şifreli görüntü kaydedildi: test_encrypted.png")
    
    # Deşifrele
    print("\nDeşifreleme başlıyor...")
    original = cv2.imread("test_original.png", cv2.IMREAD_GRAYSCALE)
    decrypted = decrypt_image(encrypted, base_key, original)
    cv2.imwrite("test_decrypted.png", decrypted)
    print(f"Deşifreli görüntü kaydedildi: test_decrypted.png")
    
    # Doğrulama
    mse = np.mean((original - decrypted) ** 2)
    print(f"\nMSE (Mean Squared Error): {mse}")
    
    if mse == 0:
        print("✅ Deşifreleme BAŞARILI!")
    else:
        print(f"❌ Deşifreleme BAŞARISIZ! (MSE={mse})")
    
    # Görsel karşılaştırma
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].imshow(original, cmap='gray')
    axes[0].set_title('Orijinal', fontsize=14, fontweight='bold')
    axes[0].axis('off')
    
    axes[1].imshow(encrypted, cmap='gray')
    axes[1].set_title('Şifreli', fontsize=14, fontweight='bold')
    axes[1].axis('off')
    
    axes[2].imshow(decrypted, cmap='gray')
    axes[2].set_title('Deşifreli', fontsize=14, fontweight='bold')
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.savefig('encryption_demo.png', dpi=200)
    print("\nGörsel karşılaştırma kaydedildi: encryption_demo.png")
    plt.show()
    
    print("\n" + "="*60)
