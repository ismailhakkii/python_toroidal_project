"""
ChaosPolybius-2026 - Numba ile Hızlandırılmış Yardımcı Fonksiyonlar

Mevcut sistemi bozmadan, kritik döngüleri numba ile optimize eder.
"""

import numpy as np
from numba import jit

@jit(nopython=True)
def fast_permutation_apply(flat_img, path_flat_indices):
    """
    Permütasyon işlemini numba ile hızlandır
    
    Args:
        flat_img: Düzleştirilmiş görüntü
        path_flat_indices: DFS yolundan gelen indeksler (flattened)
    
    Returns:
        Permütasyon uygulanmış array
    """
    N = len(flat_img)
    permuted = np.zeros(N, dtype=np.uint8)
    
    for i in range(N):
        orig_idx = path_flat_indices[i]
        permuted[i] = flat_img[orig_idx]
    
    return permuted


@jit(nopython=True)
def fast_inverse_permutation_apply(permuted_flat, path_flat_indices):
    """
    Ters permütasyonu numba ile hızlandır
    """
    N = len(permuted_flat)
    decrypted = np.zeros(N, dtype=np.uint8)
    
    for i in range(N):
        orig_idx = path_flat_indices[i]
        decrypted[orig_idx] = permuted_flat[i]
    
    return decrypted


@jit(nopython=True)
def fast_xor_diffusion(substituted_flat, key_stream):
    """
    XOR zincirleme difüzyonunu numba ile hızlandır
    """
    N = len(substituted_flat)
    encrypted = np.zeros(N, dtype=np.uint8)
    prev = np.uint8(0)
    
    for i in range(N):
        encrypted[i] = substituted_flat[i] ^ key_stream[i] ^ prev
        prev = encrypted[i]
    
    return encrypted


@jit(nopython=True)
def fast_inverse_xor_diffusion(flat_encrypted, key_stream):
    """
    Ters XOR difüzyonunu numba ile hızlandır
    """
    N = len(flat_encrypted)
    substituted = np.zeros(N, dtype=np.uint8)
    prev = np.uint8(0)
    
    for i in range(N):
        substituted[i] = flat_encrypted[i] ^ key_stream[i] ^ prev
        prev = flat_encrypted[i]
    
    return substituted


# İsteğe bağlı: S-Box işlemlerini de hızlandırabiliriz
@jit(nopython=True)
def fast_sbox_substitute(data, sbox):
    """
    S-Box substitution'ı hızlandır
    """
    N = len(data)
    result = np.zeros(N, dtype=np.uint8)
    
    for i in range(N):
        result[i] = sbox[data[i]]
    
    return result


@jit(nopython=True)
def fast_sbox_inverse(data, inverse_sbox):
    """
    Ters S-Box'ı hızlandır
    """
    N = len(data)
    result = np.zeros(N, dtype=np.uint8)
    
    for i in range(N):
        result[i] = inverse_sbox[data[i]]
    
    return result


if __name__ == "__main__":
    # Test
    print("Numba fonksiyonları hazır!")
    
    # Basit test
    test_data = np.random.randint(0, 256, 1000, dtype=np.uint8)
    test_indices = np.arange(1000, dtype=np.int32)
    np.random.shuffle(test_indices)
    test_key = np.random.randint(0, 256, 1000, dtype=np.uint8)
    
    # İlk çalıştırma (JIT compilation)
    result = fast_permutation_apply(test_data, test_indices)
    print(f"✅ Test başarılı! {len(result)} eleman işlendi.")
