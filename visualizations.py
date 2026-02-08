"""
Visualization Scripts - Görselleştirme Araçları

Rapordaki görselleri oluşturmak için kullanılır:
1. Histogram karşılaştırma
2. Korelasyon scatter plotları
3. Toroidal graf yapısı
"""

import matplotlib.pyplot as plt
import numpy as np
import cv2


def plot_histogram_comparison(original_path, encrypted_path, save_path="histogram_comparison.png"):
    """
    Orijinal vs Şifreli histogram karşılaştırması
    
    Args:
    original_path : str - Orijinal görüntü yolu
    encrypted_path : str - Şifreli görüntü yolu
    save_path : str - Çıktı dosyası
    """
    original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
    encrypted = cv2.imread(encrypted_path, cv2.IMREAD_GRAYSCALE)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Orijinal görüntü
    axes[0, 0].imshow(original, cmap='gray')
    axes[0, 0].set_title('Orijinal Görüntü', fontsize=14, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Orijinal histogram
    axes[0, 1].hist(original.ravel(), 256, [0,256], color='blue', alpha=0.7)
    axes[0, 1].set_title('Orijinal Histogram (Düzensiz)', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Piksel Değeri', fontsize=12)
    axes[0, 1].set_ylabel('Frekans', fontsize=12)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Şifreli görüntü
    axes[1, 0].imshow(encrypted, cmap='gray')
    axes[1, 0].set_title('Şifreli Görüntü', fontsize=14, fontweight='bold')
    axes[1, 0].axis('off')
    
    # Şifreli histogram
    axes[1, 1].hist(encrypted.ravel(), 256, [0,256], color='red', alpha=0.7)
    axes[1, 1].set_title('Şifreli Histogram (Uniform)', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Piksel Değeri', fontsize=12)
    axes[1, 1].set_ylabel('Frekans', fontsize=12)
    
    # İdeal uniform çizgisi
    ideal_freq = original.size / 256
    axes[1, 1].axhline(y=ideal_freq, color='green', linestyle='--', 
                       linewidth=2, label='İdeal Uniform')
    axes[1, 1].legend(fontsize=11)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('ChaosPolybius-2026: Histogram Analizi', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Histogram karşılaştırması kaydedildi: {save_path}")
    plt.close()


def plot_correlation_scatter(original_path, encrypted_path, save_path="correlation_scatter.png"):
    """
    Korelasyon scatter plotları
    
    Args:
    original_path : str
    encrypted_path : str
    save_path : str
    """
    original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
    encrypted = cv2.imread(encrypted_path, cv2.IMREAD_GRAYSCALE)
    
    H, W = original.shape
    N = 3000
    
    # Rastgele piksel çiftleri seç (yatay komşular)
    x = np.random.randint(0, H, N)
    y = np.random.randint(0, W-1, N)
    
    orig_A = original[x, y]
    orig_B = original[x, y+1]
    
    enc_A = encrypted[x, y]
    enc_B = encrypted[x, y+1]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Orijinal
    corr_orig = np.corrcoef(orig_A, orig_B)[0,1]
    ax1.scatter(orig_A, orig_B, s=2, alpha=0.5, color='blue')
    ax1.set_title(f'Orijinal Görüntü\nKorelasyon: r = {corr_orig:.4f}', 
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Piksel değeri', fontsize=12)
    ax1.set_ylabel('Komşu piksel değeri', fontsize=12)
    ax1.set_xlim(0, 255)
    ax1.set_ylim(0, 255)
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    # Şifreli
    corr_enc = np.corrcoef(enc_A, enc_B)[0,1]
    ax2.scatter(enc_A, enc_B, s=2, alpha=0.5, color='red')
    ax2.set_title(f'Şifreli Görüntü\nKorelasyon: r = {corr_enc:.4f}', 
                  fontsize=14, fontweight='bold')
    ax2.set_xlabel('Piksel değeri', fontsize=12)
    ax2.set_ylabel('Komşu piksel değeri', fontsize=12)
    ax2.set_xlim(0, 255)
    ax2.set_ylim(0, 255)
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    
    plt.suptitle('ChaosPolybius-2026: Korelasyon Analizi (Yatay Komşular)', 
                 fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Korelasyon scatter plot kaydedildi: {save_path}")
    plt.close()


def plot_lyapunov_spectrum(save_path="lyapunov_spectrum.png"):
    """
    FPLM'nin Lyapunov spektrumunu çiz
    r parametresine göre Lyapunov üssünün değişimi
    """
    from fplm import FPLM
    
    print("Lyapunov spektrumu hesaplanıyor (bu birkaç dakika sürebilir)...")
    
    r_values = np.linspace(3.57, 4.0, 100)
    lyapunov_values = []
    
    for r in r_values:
        fplm = FPLM(x0=0.5, u0=0.3, r=r, a=0.2, b=0.3, c=0.4, delta=0.1)
        lyap = fplm.lyapunov_exponent(n_iterations=5000, n_discard=500)
        lyapunov_values.append(lyap)
    
    # Grafik
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(r_values, lyapunov_values, 'b-', linewidth=2, label='FPLM')
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, label='λ = 0 (Kaos Sınırı)')
    ax.fill_between(r_values, 0, lyapunov_values, 
                     where=np.array(lyapunov_values) > 0, 
                     alpha=0.3, color='green', label='Kaotik Bölge (λ > 0)')
    
    ax.set_xlabel('r (Bifurkasyon Parametresi)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Lyapunov Üssü (λ)', fontsize=13, fontweight='bold')
    ax.set_title('FPLM Lyapunov Spektrumu\nPeriyodik Pencerelerin Kapatıldığı Gösterildi', 
                 fontsize=15, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Lyapunov spektrumu kaydedildi: {save_path}")
    plt.close()


def plot_bifurcation_diagram(save_path="bifurcation_diagram.png"):
    """
    Bifurkasyon diyagramı - FPLM'nin kararlılığını gösterir
    """
    from fplm import FPLM
    
    print("Bifurkasyon diyagramı hesaplanıyor...")
    
    r_values = np.linspace(3.57, 4.0, 400)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for r in r_values:
        fplm = FPLM(x0=0.5, u0=0.3, r=r, a=0.2, b=0.3, c=0.4, delta=0.1)
        
        # Transient'ı at
        fplm.iterate(1000, discard=0)
        
        # Son 100 değeri topla
        values, _ = fplm.iterate(100, discard=0)
        
        # Scatter plot
        ax.plot([r]*len(values), values, 'b,', markersize=1, alpha=0.5)
    
    ax.set_xlabel('r (Bifurkasyon Parametresi)', fontsize=13, fontweight='bold')
    ax.set_ylabel('x (Sistem Durumu)', fontsize=13, fontweight='bold')
    ax.set_title('FPLM Bifurkasyon Diyagramı\n(Geri Besleme + Pertürbasyon ile Düzgünleştirilmiş)', 
                 fontsize=15, fontweight='bold')
    ax.set_xlim(3.57, 4.0)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Bifurkasyon diyagramı kaydedildi: {save_path}")
    plt.close()


def create_all_visualizations():
    """Tüm görselleri oluştur"""
    print("="*70)
    print("TÜM GÖRSELLEŞTİRMELER OLUŞTURULUYOR")
    print("="*70)
    
    # 1. Histogram
    if os.path.exists("test_image.png") and os.path.exists("encrypted.png"):
        print("\n[1/5] Histogram karşılaştırması...")
        plot_histogram_comparison("test_image.png", "encrypted.png")
    else:
        print("\n[1/5] Histogram için gerekli dosyalar bulunamadı (test_image.png, encrypted.png)")
    
    # 2. Korelasyon
    if os.path.exists("test_image.png") and os.path.exists("encrypted.png"):
        print("\n[2/5] Korelasyon scatter plot...")
        plot_correlation_scatter("test_image.png", "encrypted.png")
    else:
        print("\n[2/5] Korelasyon için gerekli dosyalar bulunamadı")
    
    # 3. Lyapunov spektrumu
    print("\n[3/5] Lyapunov spektrumu...")
    plot_lyapunov_spectrum()
    
    # 4. Bifurkasyon diyagramı
    print("\n[4/5] Bifurkasyon diyagramı...")
    plot_bifurcation_diagram()
    
    # 5. Toroidal DFS (modülün kendi test kodu çalıştırılabilir)
    print("\n[5/5] Toroidal DFS görselleştirmesi için toroidal_dfs.py çalıştırın")
    
    print("\n" + "="*70)
    print("TÜM GÖRSELLEŞTİRMELER TAMAMLANDI")
    print("="*70)
    print("\nOluşturulan dosyalar:")
    print("  - histogram_comparison.png")
    print("  - correlation_scatter.png")
    print("  - lyapunov_spectrum.png")
    print("  - bifurcation_diagram.png")
    print("\n" + "="*70)


if __name__ == "__main__":
    import os
    create_all_visualizations()
