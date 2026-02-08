"""
Dynamic Polybius Square (Dinamik S-Box)

Rapordaki Bölüm 4.3'ü uygular.
Her oturumda FPLM ile karıştırılan 8x8 Polybius matrisi.
"""

import numpy as np
from fplm import FPLM


class DynamicPolybius:
    """
    Anahtar-Bağımlı Dinamik Polybius Matrisi (8x8 S-Box)
    
    Standart Polybius karesi yerine her şifrelemede FPLM ile
    karıştırılan dinamik bir substitution box kullanır.
    """
    
    def __init__(self, fplm, size=16):
        """
        Args:
        fplm : FPLM nesnesi
        size : S-Box boyutu (16x16 = 256 karakter)
        """
        self.fplm = fplm
        self.size = size
        self.sbox = None
        self.inverse_sbox = None
        
        # S-Box'ı oluştur
        self.generate_sbox()
    
    def generate_sbox(self):
        """
        FPLM kullanarak dinamik S-Box oluştur
        
        256 elemanlı bir array oluşturulur ve FPLM'den gelen
        kaotik sayılarla Fisher-Yates shuffle algoritması ile karıştırılır.
        """
        # 0-255 arası tüm byte değerlerini içeren array
        self.sbox = np.arange(256, dtype=np.uint8)
        
        # Fisher-Yates shuffle (FPLM destekli)
        for i in range(255, 0, -1):
            # FPLM'den rastgele indeks
            rand_val = self.fplm.step()
            j = int(rand_val * (i + 1)) % (i + 1)
            
            # Swap
            self.sbox[i], self.sbox[j] = self.sbox[j], self.sbox[i]
        
        # Ters S-Box oluştur (deşifreleme için)
        self.inverse_sbox = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            self.inverse_sbox[self.sbox[i]] = i
    
    def substitute(self, data):
        """
        S-Box ile substitution yap
        
        Args:
        data : numpy array (uint8)
        
        Returns:
        numpy array: Substitute edilmiş veri
        """
        return self.sbox[data]
    
    def inverse_substitute(self, data):
        """
        Ters S-Box ile substitution'ı geri al
        
        Args:
        data : numpy array (uint8)
        
        Returns:
        numpy array: Orijinal veri
        """
        return self.inverse_sbox[data]
    
    def get_sbox_matrix(self):
        """
        S-Box'ı 16x16 matris olarak döndür (görselleştirme için)
        
        Returns:
        numpy array: 16x16 matris
        """
        return self.sbox.reshape(16, 16)
    
    def avalanche_effect(self):
        """
        Avalanche Effect'i test et
        Tek bit değişiminin ortalama kaç bit değişimine neden olduğunu ölç
        
        Returns:
        float: Ortalama değişen bit sayısı (ideal: 4.0 bit = %50)
        """
        total_changed_bits = 0
        test_count = 256
        
        for val in range(test_count):
            original = np.uint8(val)
            substituted = self.sbox[original]
            
            # 1 bit değiştir
            flipped = original ^ 1  # İlk biti flip et
            substituted_flipped = self.sbox[flipped]
            
            # Kaç bit değişti?
            xor_result = substituted ^ substituted_flipped
            changed_bits = bin(xor_result).count('1')
            
            total_changed_bits += changed_bits
        
        avg_changed_bits = total_changed_bits / test_count
        
        return avg_changed_bits
    
    def nonlinearity(self):
        """
        S-Box'ın doğrusal olmama (nonlinearity) derecesini ölç
        
        Returns:
        float: Nonlinearity skoru (yüksek = iyi)
        """
        # Walsh spektrum analizi (basitleştirilmiş)
        walsh_values = []
        
        for a in range(1, 256, 16):  # Her 16'da bir test et (hız için)
            walsh_sum = 0
            for x in range(256):
                fx = self.sbox[x]
                parity = bin((a & x) ^ fx).count('1') % 2
                walsh_sum += (-1) ** parity
            
            walsh_values.append(abs(walsh_sum))
        
        max_walsh = max(walsh_values)
        nonlinearity = 128 - (max_walsh / 2)
        
        return nonlinearity
    
    def visualize_sbox(self, save_path=None):
        """
        S-Box'ı görselleştir
        
        Args:
        save_path : Kayıt yolu (opsiyonel)
        """
        import matplotlib.pyplot as plt
        
        sbox_matrix = self.get_sbox_matrix()
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Sol: S-Box heatmap
        im1 = axes[0].imshow(sbox_matrix, cmap='viridis', interpolation='nearest')
        axes[0].set_title('Dinamik S-Box (16x16)\nFPLM ile Karıştırılmış', 
                         fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Sütun')
        axes[0].set_ylabel('Satır')
        plt.colorbar(im1, ax=axes[0], label='Byte Değeri')
        
        # Grid ekle
        for i in range(17):
            axes[0].axhline(y=i-0.5, color='white', linewidth=0.5, alpha=0.3)
            axes[0].axvline(x=i-0.5, color='white', linewidth=0.5, alpha=0.3)
        
        # Sağ: S-Box değerlerinin dağılımı
        axes[1].hist(self.sbox, bins=32, color='purple', alpha=0.7, edgecolor='black')
        axes[1].set_title('S-Box Değer Dağılımı', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Değer Aralığı')
        axes[1].set_ylabel('Frekans')
        axes[1].grid(True, alpha=0.3)
        
        # Uniform olmalı
        axes[1].axhline(y=8, color='red', linestyle='--', 
                       linewidth=2, label='İdeal Uniform (8 per bin)')
        axes[1].legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"S-Box görseli kaydedildi: {save_path}")
        
        plt.show()
    
    def __repr__(self):
        return f"DynamicPolybius(size={self.size}x{self.size}, elements={self.size**2})"


if __name__ == "__main__":
    # Test kodu
    print("="*60)
    print("Dynamic Polybius S-Box Test")
    print("="*60)
    
    # FPLM oluştur
    fplm = FPLM(x0=0.123, u0=0.456, r=3.99)
    
    # Dinamik S-Box oluştur
    sbox = DynamicPolybius(fplm)
    
    print(f"\nS-Box oluşturuldu: {sbox}")
    
    # İlk 16 S-Box değerini göster
    print(f"\nİlk 16 S-Box değeri:")
    print(f"  Input:  {list(range(16))}")
    print(f"  Output: {list(sbox.sbox[:16])}")
    
    # Substitution testi
    test_data = np.array([0, 1, 2, 3, 4, 5, 255], dtype=np.uint8)
    substituted = sbox.substitute(test_data)
    recovered = sbox.inverse_substitute(substituted)
    
    print(f"\nSubstitution Testi:")
    print(f"  Orijinal:    {test_data}")
    print(f"  Substitute:  {substituted}")
    print(f"  Recovered:   {recovered}")
    print(f"  Başarılı mı? {np.array_equal(test_data, recovered)}")
    
    # Avalanche Effect
    avalanche = sbox.avalanche_effect()
    print(f"\nAvalanche Effect:")
    print(f"  Ortalama değişen bit: {avalanche:.2f} / 8")
    print(f"  Yüzde: {(avalanche/8)*100:.1f}%")
    print(f"  İdeal: 4.0 bit (%50)")
    
    if avalanche >= 3.5:
        print("  ✅ Avalanche testi GEÇTI")
    else:
        print("  ❌ Avalanche testi BAŞARISIZ")
    
    # Nonlinearity
    nonlin = sbox.nonlinearity()
    print(f"\nNonlinearity:")
    print(f"  Skor: {nonlin:.2f}")
    print(f"  İdeal: >100")
    
    if nonlin > 100:
        print("  ✅ Nonlinearity testi GEÇTI")
    else:
        print("  ⚠️  Nonlinearity düşük")
    
    # Görselleştir
    print("\nS-Box görselleştiriliyor...")
    sbox.visualize_sbox("sbox_visualization.png")
    
    print("\n" + "="*60)
