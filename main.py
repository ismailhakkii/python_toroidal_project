"""
ChaosPolybius-2026 - Ana Test ve Demo Programı

Bu script, tüm sistemi test eder ve rapordaki Tablo 1'deki sonuçları üretir.

Testler:
1. Şifreleme/Deşifreleme Testi
2. NPCR/UACI Testi (Diferansiyel Analiz)
3. Entropi ve Korelasyon Analizi
4. Performans Testi
"""

import cv2
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from encryption import encrypt_image, decrypt_image, encrypt_image_from_array
from security_metrics import SecurityMetrics


def create_test_image(size=(256, 256), save_path="test_image.png"):
    """Test için Lena benzeri yapısal görüntü oluştur"""
    H, W = size
    img = np.zeros((H, W), dtype=np.uint8)
    
    # Gradyan ve sinüzoidal pattern oluştur
    for i in range(H):
        for j in range(W):
            img[i, j] = int((i * 0.5 + j * 0.5 + 
                           50 * np.sin(i/10) + 
                           50 * np.cos(j/10)) % 256)
    
    cv2.imwrite(save_path, img)
    print(f"Test görüntüsü oluşturuldu: {save_path}")
    return img


def test_encryption_decryption(image_path, base_key):
    """Test 1: Şifreleme/Deşifreleme"""
    print("\n" + "="*70)
    print("[TEST 1] ŞİFRELEME/DEŞİFRELEME TESTİ")
    print("="*70)
    
    # Orijinal görüntüyü yükle
    original = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    print(f"Görüntü boyutu: {original.shape}")
    
    # Şifrele
    print("\nŞifreleme başlıyor...")
    start = time.time()
    encrypted = encrypt_image(image_path, base_key)
    enc_time = (time.time() - start) * 1000
    
    cv2.imwrite("encrypted.png", encrypted)
    print(f"✓ Şifreleme tamamlandı: {enc_time:.2f} ms")
    
    # Deşifrele
    print("\nDeşifreleme başlıyor...")
    start = time.time()
    decrypted = decrypt_image(encrypted, base_key, original)
    dec_time = (time.time() - start) * 1000
    
    cv2.imwrite("decrypted.png", decrypted)
    print(f"✓ Deşifreleme tamamlandı: {dec_time:.2f} ms")
    
    # Doğrulama
    mse = np.mean((original - decrypted) ** 2)
    print(f"\nMSE (Mean Squared Error): {mse}")
    
    if mse == 0:
        print("✅ DEŞİFRELEME BAŞARILI - Orijinal görüntü tamamen geri kazanıldı!")
    else:
        print(f"❌ DEŞİFRELEME BAŞARISIZ - MSE: {mse}")
    
    return original, encrypted, decrypted


def test_differential_analysis(original, base_key):
    """Test 2: NPCR/UACI (Diferansiyel Analiz)"""
    print("\n" + "="*70)
    print("[TEST 2] DİFERANSİYEL ANALİZ (NPCR/UACI)")
    print("="*70)
    
    # 1 piksel değiştir
    modified = original.copy()
    modified[0, 0] = np.uint8((int(modified[0, 0]) + 1) % 256)
    print(f"Piksel [0,0] değiştirildi: {original[0,0]} → {modified[0,0]}")
    
    # İki farklı şifreli görüntü üret
    encrypted1 = encrypt_image_from_array(original, base_key)
    encrypted2 = encrypt_image_from_array(modified, base_key)
    
    # NPCR hesapla
    npcr = SecurityMetrics.npcr(encrypted1, encrypted2)
    print(f"\nNPCR: {npcr:.4f}%")
    print(f"Hedef: >99.6094%")
    
    if npcr > 99.60:
        print("✅ NPCR testi GEÇTI")
    else:
        print("❌ NPCR testi BAŞARISIZ")
    
    # UACI hesapla
    uaci = SecurityMetrics.uaci(encrypted1, encrypted2)
    print(f"\nUACI: {uaci:.4f}%")
    print(f"Hedef: 33.28% - 33.64%")
    
    if 33.28 < uaci < 33.64:
        print("✅ UACI testi GEÇTI")
    else:
        print("⚠️  UACI sınırlar dışında")
    
    # Tablo 1 formatında göster
    print("\n" + "-"*70)
    print("TABLO 1: Güvenlik Analizi Karşılaştırması")
    print("-"*70)
    print(f"{'Metrik':<20} {'İdeal':<15} {'ChaosPolybius-2026':<20}")
    print("-"*70)
    print(f"{'NPCR (%)':<20} {'99.6094':<15} {npcr:<20.4f}")
    print(f"{'UACI (%)':<20} {'33.4635':<15} {uaci:<20.4f}")
    print("-"*70)
    
    return npcr, uaci


def test_statistical_analysis(original, encrypted):
    """Test 3: İstatistiksel Analiz (Entropi, Korelasyon)"""
    print("\n" + "="*70)
    print("[TEST 3] İSTATİSTİKSEL ANALİZ")
    print("="*70)
    
    # Entropi
    print("\n[3.1] ENTROPİ ANALİZİ")
    print("-"*70)
    entropy_orig = SecurityMetrics.entropy(original)
    entropy_enc = SecurityMetrics.entropy(encrypted)
    
    print(f"Orijinal görüntü entropisi: {entropy_orig:.4f} bit")
    print(f"Şifreli görüntü entropisi:  {entropy_enc:.4f} bit")
    print(f"Hedef:                       8.0000 bit")
    
    if entropy_enc > 7.99:
        print("✅ Entropi testi GEÇTI")
    else:
        print("⚠️  Entropi düşük")
    
    # Korelasyon
    print("\n[3.2] KORELASYON ANALİZİ")
    print("-"*70)
    
    corr_orig_h = SecurityMetrics.correlation(original, 'horizontal')
    corr_orig_v = SecurityMetrics.correlation(original, 'vertical')
    corr_orig_d = SecurityMetrics.correlation(original, 'diagonal')
    
    corr_enc_h = SecurityMetrics.correlation(encrypted, 'horizontal')
    corr_enc_v = SecurityMetrics.correlation(encrypted, 'vertical')
    corr_enc_d = SecurityMetrics.correlation(encrypted, 'diagonal')
    
    print("Orijinal görüntü:")
    print(f"  Yatay korelasyon:   {corr_orig_h:.4f}")
    print(f"  Dikey korelasyon:   {corr_orig_v:.4f}")
    print(f"  Çapraz korelasyon:  {corr_orig_d:.4f}")
    
    print("\nŞifreli görüntü:")
    print(f"  Yatay korelasyon:   {corr_enc_h:.4f}")
    print(f"  Dikey korelasyon:   {corr_enc_v:.4f}")
    print(f"  Çapraz korelasyon:  {corr_enc_d:.4f}")
    print(f"  Hedef:              0.0000")
    
    avg_corr = np.mean([abs(corr_enc_h), abs(corr_enc_v), abs(corr_enc_d)])
    
    if avg_corr < 0.01:
        print("✅ Korelasyon testi GEÇTI")
    else:
        print("⚠️  Korelasyon yüksek")
    
    # Chi-square
    print("\n[3.3] CHI-SQUARE UNİFORMİTY TEST")
    print("-"*70)
    
    chi_result = SecurityMetrics.chi_square_test(encrypted)
    
    print(f"χ² değeri:        {chi_result['chi_square']:.2f}")
    print(f"Kritik değer:     {chi_result['critical_value']:.2f}")
    print(f"p-değeri:         {chi_result['p_value']:.4f}")
    print(f"Serbestlik der.:  {chi_result['df']}")
    
    if chi_result['passed']:
        print("✅ Chi-square testi GEÇTI")
    else:
        print("❌ Chi-square testi BAŞARISIZ")
    
    return entropy_enc, corr_enc_h


def test_performance(base_key):
    """Test 4: Performans Analizi"""
    print("\n" + "="*70)
    print("[TEST 4] PERFORMANS ANALİZİ")
    print("="*70)
    
    sizes = [(128, 128), (256, 256), (512, 512)]
    
    print(f"\n{'Boyut':<15} {'Şifreleme':<20} {'Throughput':<20}")
    print("-"*70)
    
    for h, w in sizes:
        # Test görüntüsü oluştur
        test_img = np.random.randint(0, 256, (h, w), dtype=np.uint8)
        
        # Şifreleme süresini ölç
        start = time.time()
        enc = encrypt_image_from_array(test_img, base_key)
        enc_time = (time.time() - start) * 1000
        
        # Throughput hesapla (MB/s)
        data_size_mb = (h * w) / (1024 * 1024)
        throughput = data_size_mb / (enc_time / 1000)
        
        print(f"{h}×{w:<10} {enc_time:<18.2f} ms {throughput:<18.2f} MB/s")
    
    print("-"*70)


def visualize_results(original, encrypted, decrypted):
    """Sonuçları görselleştir"""
    print("\n" + "="*70)
    print("GÖRSEL SONUÇLAR OLUŞTURULUYOR")
    print("="*70)
    
    # Ana görselleştirme
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Görüntüler
    axes[0, 0].imshow(original, cmap='gray')
    axes[0, 0].set_title('Orijinal Görüntü', fontsize=14, fontweight='bold')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(encrypted, cmap='gray')
    axes[0, 1].set_title('Şifreli Görüntü', fontsize=14, fontweight='bold')
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(decrypted, cmap='gray')
    axes[0, 2].set_title('Deşifreli Görüntü', fontsize=14, fontweight='bold')
    axes[0, 2].axis('off')
    
    # Histogramlar
    axes[1, 0].hist(original.ravel(), bins=256, range=[0,256], color='blue', alpha=0.7)
    axes[1, 0].set_title('Orijinal Histogram', fontsize=12)
    axes[1, 0].set_xlabel('Piksel Değeri')
    axes[1, 0].set_ylabel('Frekans')
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].hist(encrypted.ravel(), bins=256, range=[0,256], color='red', alpha=0.7)
    axes[1, 1].set_title('Şifreli Histogram (Uniform)', fontsize=12)
    axes[1, 1].set_xlabel('Piksel Değeri')
    axes[1, 1].set_ylabel('Frekans')
    ideal_freq = (original.size) / 256
    axes[1, 1].axhline(y=ideal_freq, color='green', linestyle='--', linewidth=2, label='İdeal')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    axes[1, 2].hist(decrypted.ravel(), bins=256, range=[0,256], color='purple', alpha=0.7)
    axes[1, 2].set_title('Deşifreli Histogram', fontsize=12)
    axes[1, 2].set_xlabel('Piksel Değeri')
    axes[1, 2].set_ylabel('Frekans')
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test_results.png', dpi=300, bbox_inches='tight')
    print("✓ Görsel kaydedildi: test_results.png")
    plt.close()


def main():
    """Ana test fonksiyonu"""
    print("\n" + "="*70)
    print(" "*15 + "ChaosPolybius-2026")
    print(" "*8 + "Kaotik Hibrit Görüntü Şifreleme Sistemi")
    print(" "*20 + "Test Programı")
    print("="*70)
    
    # Anahtar parametreleri (Rapordaki değerler)
    base_key = [0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1]
    print(f"\nAnahtar: {base_key}")
    
    # Test görüntüsü oluştur veya mevcut görüntüyü kullan
    image_path = "test_image.png"
    
    if not os.path.exists(image_path):
        print(f"\n'{image_path}' bulunamadı, test görüntüsü oluşturuluyor...")
        create_test_image(size=(256, 256), save_path=image_path)
    
    # Testleri çalıştır
    try:
        original, encrypted, decrypted = test_encryption_decryption(image_path, base_key)
        npcr, uaci = test_differential_analysis(original, base_key)
        entropy, correlation = test_statistical_analysis(original, encrypted)
        test_performance(base_key)
        
        # Görselleştirme
        visualize_results(original, encrypted, decrypted)
        
        # Özet Rapor
        print("\n" + "="*70)
        print("ÖZET RAPOR")
        print("="*70)
        print(f"NPCR:          {npcr:.4f}% (Hedef: >99.60%)")
        print(f"UACI:          {uaci:.4f}% (Hedef: ~33.46%)")
        print(f"Entropi:       {entropy:.4f} bit (Hedef: 8.00)")
        print(f"Korelasyon:    {abs(correlation):.4f} (Hedef: 0.00)")
        print("="*70)
        
        # Final değerlendirme
        all_passed = (npcr > 99.60 and 
                      33.28 < uaci < 33.64 and 
                      entropy > 7.99 and 
                      abs(correlation) < 0.01)
        
        if all_passed:
            print("\n✅ TÜM TESTLER BAŞARIYLA GEÇTİ!")
            print("Sistem rapordaki güvenlik standartlarını karşılamaktadır.")
        else:
            print("\n⚠️  Bazı testler beklenenden farklı sonuçlar verdi.")
        
        print("\nOluşturulan dosyalar:")
        print("  - encrypted.png (Şifreli görüntü)")
        print("  - decrypted.png (Deşifreli görüntü)")
        print("  - test_results.png (Görsel karşılaştırma)")
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("TEST TAMAMLANDI")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
