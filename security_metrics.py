"""
Security Metrics - Güvenlik Metrikleri Modülü

Rapordaki Tablo 1'deki metrikleri hesaplar:
- NPCR (Number of Pixels Change Rate)
- UACI (Unified Average Changing Intensity)
- Entropi
- Korelasyon
- Chi-Square Test
"""

import numpy as np
import cv2
from scipy import stats


class SecurityMetrics:
    """
    Görüntü şifreleme güvenlik metrikleri
    """
    
    @staticmethod
    def npcr(img1, img2):
        """
        Number of Pixels Change Rate (NPCR)
        
        Tek piksel değişiminin kaç piksel değişimine neden olduğunu ölçer.
        İdeal değer: %99.6094 (256x256 görüntü için)
        
        Args:
        img1, img2 : numpy.ndarray - Karşılaştırılacak görüntüler
        
        Returns:
        float: NPCR yüzdesi
        """
        if img1.shape != img2.shape:
            raise ValueError("Görüntüler aynı boyutta olmalı")
        
        # Farklı olan piksel sayısı
        diff = (img1 != img2).astype(int)
        
        npcr_value = (np.sum(diff) / img1.size) * 100
        
        return npcr_value
    
    @staticmethod
    def uaci(img1, img2):
        """
        Unified Average Changing Intensity (UACI)
        
        Piksel değişimlerinin ortalama yoğunluğunu ölçer.
        İdeal değer: %33.4635 (8-bit görüntü için)
        
        Args:
        img1, img2 : numpy.ndarray
        
        Returns:
        float: UACI yüzdesi
        """
        if img1.shape != img2.shape:
            raise ValueError("Görüntüler aynı boyutta olmalı")
        
        # Mutlak farkları hesapla
        abs_diff = np.abs(img1.astype(float) - img2.astype(float))
        
        # UACI formülü
        uaci_value = (np.sum(abs_diff) / (255 * img1.size)) * 100
        
        return uaci_value
    
    @staticmethod
    def entropy(image):
        """
        Shannon Entropisi
        
        Bilgi entropisi. Görüntünün rastgelelik derecesini ölçer.
        İdeal değer: 8.0 (8-bit görüntü için)
        
        Args:
        image : numpy.ndarray
        
        Returns:
        float: Entropi değeri (bit)
        """
        # Histogram hesapla
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist = hist.ravel() / hist.sum()  # Normalize et
        
        # Sıfır olmayan olasılıkları al
        hist = hist[hist > 0]
        
        # Shannon entropisi: H = -Σ p(i) * log2(p(i))
        entropy_value = -np.sum(hist * np.log2(hist))
        
        return entropy_value
    
    @staticmethod
    def correlation(image, direction='horizontal', sample_size=3000):
        """
        Komşu Piksel Korelasyon Katsayısı
        
        Komşu pikseller arasındaki ilişkiyi ölçer.
        İdeal değer: 0.0 (tamamen ilişkisiz)
        Orijinal görüntülerde genellikle 0.9+ olur.
        
        Args:
        image : numpy.ndarray
        direction : str - 'horizontal', 'vertical', 'diagonal'
        sample_size : int - Rastgele kaç piksel çifti test edilecek
        
        Returns:
        float: Korelasyon katsayısı [-1, 1]
        """
        H, W = image.shape
        
        # Rastgele piksel çiftleri seç
        if direction == 'horizontal':
            x = np.random.randint(0, H, sample_size)
            y = np.random.randint(0, W-1, sample_size)
            A = image[x, y].astype(float)
            B = image[x, y+1].astype(float)
        
        elif direction == 'vertical':
            x = np.random.randint(0, H-1, sample_size)
            y = np.random.randint(0, W, sample_size)
            A = image[x, y].astype(float)
            B = image[x+1, y].astype(float)
        
        elif direction == 'diagonal':
            x = np.random.randint(0, H-1, sample_size)
            y = np.random.randint(0, W-1, sample_size)
            A = image[x, y].astype(float)
            B = image[x+1, y+1].astype(float)
        
        else:
            raise ValueError("direction: 'horizontal', 'vertical', 'diagonal'")
        
        # Korelasyon formülü
        mean_A = np.mean(A)
        mean_B = np.mean(B)
        
        numerator = np.sum((A - mean_A) * (B - mean_B))
        denominator = np.sqrt(
            np.sum((A - mean_A)**2) * np.sum((B - mean_B)**2)
        )
        
        if denominator == 0:
            return 0.0
        
        correlation = numerator / denominator
        
        return correlation
    
    @staticmethod
    def chi_square_test(image, alpha=0.05):
        """
        Chi-Square Uniformity Test
        
        Piksellerin uniform dağılıma ne kadar uyduğunu test eder.
        
        Args:
        image : numpy.ndarray
        alpha : float - Anlamlılık seviyesi (varsayılan: 0.05)
        
        Returns:
        dict: Test sonuçları
        """
        # Histogram
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist = hist.ravel()
        
        # Beklenen değer (uniform dağılım)
        expected = image.size / 256
        
        # Chi-square istatistiği: χ² = Σ[(O - E)² / E]
        chi_square = np.sum((hist - expected)**2 / expected)
        
        # Serbestlik derecesi: df = 256 - 1 = 255
        df = 255
        
        # Kritik değer (α=0.05, df=255)
        critical_value = stats.chi2.ppf(1 - alpha, df)
        
        # p-değeri
        p_value = 1 - stats.chi2.cdf(chi_square, df)
        
        # Test sonucu
        passed = chi_square < critical_value
        
        return {
            'chi_square': chi_square,
            'critical_value': critical_value,
            'p_value': p_value,
            'df': df,
            'passed': passed
        }
    
    @staticmethod
    def key_sensitivity(encrypt_func, image, key1, key2):
        """
        Anahtar Hassasiyeti Testi
        
        Anahtar'daki minimal değişimin şifreli görüntüde büyük değişime
        neden olduğunu test eder.
        
        Args:
        encrypt_func : function - Şifreleme fonksiyonu
        image : numpy.ndarray - Test görüntüsü
        key1, key2 : Farklı anahtarlar
        
        Returns:
        dict: NPCR ve UACI sonuçları
        """
        enc1 = encrypt_func(image, key1)
        enc2 = encrypt_func(image, key2)
        
        npcr_val = SecurityMetrics.npcr(enc1, enc2)
        uaci_val = SecurityMetrics.uaci(enc1, enc2)
        
        return {
            'npcr': npcr_val,
            'uaci': uaci_val
        }
    
    @staticmethod
    def comprehensive_analysis(original, encrypted):
        """
        Kapsamlı güvenlik analizi yap
        
        Args:
        original : numpy.ndarray - Orijinal görüntü
        encrypted : numpy.ndarray - Şifreli görüntü
        
        Returns:
        dict: Tüm metrikler
        """
        results = {}
        
        # Entropi
        results['entropy_original'] = SecurityMetrics.entropy(original)
        results['entropy_encrypted'] = SecurityMetrics.entropy(encrypted)
        
        # Korelasyon
        results['correlation_original_h'] = SecurityMetrics.correlation(original, 'horizontal')
        results['correlation_original_v'] = SecurityMetrics.correlation(original, 'vertical')
        results['correlation_original_d'] = SecurityMetrics.correlation(original, 'diagonal')
        
        results['correlation_encrypted_h'] = SecurityMetrics.correlation(encrypted, 'horizontal')
        results['correlation_encrypted_v'] = SecurityMetrics.correlation(encrypted, 'vertical')
        results['correlation_encrypted_d'] = SecurityMetrics.correlation(encrypted, 'diagonal')
        
        # Chi-square
        results['chi_square_original'] = SecurityMetrics.chi_square_test(original)
        results['chi_square_encrypted'] = SecurityMetrics.chi_square_test(encrypted)
        
        return results
    
    @staticmethod
    def print_analysis(results):
        """
        Analiz sonuçlarını yazdır
        
        Args:
        results : dict - comprehensive_analysis() çıktısı
        """
        print("="*60)
        print("GÜVENLİK METRİKLERİ ANALİZİ")
        print("="*60)
        
        # Entropi
        print("\n[1] ENTROPİ")
        print("-"*60)
        print(f"Orijinal:  {results['entropy_original']:.4f} bit")
        print(f"Şifreli:   {results['entropy_encrypted']:.4f} bit")
        print(f"Hedef:     8.0000 bit")
        
        if results['entropy_encrypted'] > 7.99:
            print("✅ Entropi testi GEÇTI")
        else:
            print("❌ Entropi düşük")
        
        # Korelasyon
        print("\n[2] KORELASYON")
        print("-"*60)
        print("Orijinal Görüntü:")
        print(f"  Yatay:     {results['correlation_original_h']:.4f}")
        print(f"  Dikey:     {results['correlation_original_v']:.4f}")
        print(f"  Çapraz:    {results['correlation_original_d']:.4f}")
        
        print("\nŞifreli Görüntü:")
        print(f"  Yatay:     {results['correlation_encrypted_h']:.4f}")
        print(f"  Dikey:     {results['correlation_encrypted_v']:.4f}")
        print(f"  Çapraz:    {results['correlation_encrypted_d']:.4f}")
        print(f"  Hedef:     0.0000")
        
        avg_corr = np.mean([
            abs(results['correlation_encrypted_h']),
            abs(results['correlation_encrypted_v']),
            abs(results['correlation_encrypted_d'])
        ])
        
        if avg_corr < 0.01:
            print("✅ Korelasyon testi GEÇTI")
        else:
            print("⚠️  Korelasyon yüksek")
        
        # Chi-square
        print("\n[3] CHI-SQUARE UNİFORMİTY TEST")
        print("-"*60)
        chi_enc = results['chi_square_encrypted']
        
        print(f"χ² değeri:        {chi_enc['chi_square']:.2f}")
        print(f"Kritik değer:     {chi_enc['critical_value']:.2f}")
        print(f"p-değeri:         {chi_enc['p_value']:.4f}")
        print(f"Serbestlik der.:  {chi_enc['df']}")
        print(f"Sonuç:            {'✅ GEÇTI' if chi_enc['passed'] else '❌ BAŞARISIZ'}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # Test kodu
    print("="*60)
    print("Security Metrics Test")
    print("="*60)
    
    # Test görüntüleri oluştur
    np.random.seed(42)
    
    # Orijinal: Yapısal görüntü (yüksek korelasyon)
    original = np.zeros((256, 256), dtype=np.uint8)
    for i in range(256):
        for j in range(256):
            original[i, j] = (i + j) // 2
    
    # Şifreli: Rastgele görüntü (düşük korelasyon)
    encrypted = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
    
    # Tek piksel değişikliği
    modified = encrypted.copy()
    modified[0, 0] = (modified[0, 0] + 1) % 256
    
    # NPCR
    npcr_val = SecurityMetrics.npcr(encrypted, modified)
    print(f"\nNPCR: {npcr_val:.4f}%")
    print(f"Hedef: >99.60%")
    
    if npcr_val > 99.60:
        print("✅ NPCR testi GEÇTI")
    
    # UACI
    uaci_val = SecurityMetrics.uaci(encrypted, modified)
    print(f"\nUACI: {uaci_val:.4f}%")
    print(f"Hedef: ~33.46%")
    
    if 33.28 < uaci_val < 33.64:
        print("✅ UACI testi GEÇTI")
    
    # Kapsamlı analiz
    print("\n\nKapsamlı Analiz Yapılıyor...")
    results = SecurityMetrics.comprehensive_analysis(original, encrypted)
    SecurityMetrics.print_analysis(results)
