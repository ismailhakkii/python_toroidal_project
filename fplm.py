"""
FPLM - Feedback Perturbation Logistic Map
Geri Beslemeli Pertürbasyon ile Güçlendirilmiş Lojistik Harita

Matematiksel Model:
x_{n+1} = [r * x_n * (1 - x_n) + k * x_{n-1} * sin(π * x_n)] mod 1

Bu sistem rapordaki denklem 4.1'i uygular ve dinamik bozulmayı engeller.
"""

import numpy as np


class FPLM:
    """
    Feedback Perturbation Logistic Map (FPLM)
    
    Parametreler:
    x0 : Başlangıç değeri [0, 1]
    u0 : İkinci başlangıç değeri (geri besleme için) [0, 1]
    r  : Bifurkasyon parametresi [3.57, 4.0]
    a  : Pertürbasyon katsayısı
    b  : Geri besleme katsayısı
    c  : Dinamik modülasyon katsayısı
    delta : Periyodik pencere kapatma parametresi
    """
    
    def __init__(self, x0=0.5, u0=0.3, r=3.99, a=0.2, b=0.3, c=0.4, delta=0.1):
        # Başlangıç değerlerini normalize et
        self.x_prev = x0 % 1.0
        self.x_curr = u0 % 1.0
        
        # Sistem parametreleri
        self.r = r
        self.a = a
        self.b = b
        self.c = c
        self.delta = delta
        
        # İstatistikler
        self.iteration_count = 0
    
    def step(self):
        """
        Bir adım iterasyon yap
        
        Denklem:
        x_{n+1} = [r * x_n * (1 - x_n) + k * x_{n-1} * sin(π * x_n)] mod 1
        
        Returns:
        float: Yeni x değeri
        """
        # Standart lojistik harita terimi
        logistic_term = self.r * self.x_curr * (1 - self.x_curr)
        
        # Pertürbasyon terimi (sin ile doğrusal olmayan dürtükleme)
        perturbation = self.a * np.sin(np.pi * self.x_curr)
        
        # Geri besleme terimi (hafıza)
        feedback = self.b * self.x_prev * np.sin(np.pi * self.x_curr)
        
        # Dinamik modülasyon (periyodik pencereleri kapatma)
        modulation = self.c * np.sin(2 * np.pi * self.x_curr) * np.cos(np.pi * self.x_prev)
        
        # Yeni değer hesapla ve [0, 1] aralığında tut
        x_next = (logistic_term + perturbation + feedback + modulation + self.delta) % 1.0
        
        # Durumları güncelle
        self.x_prev = self.x_curr
        self.x_curr = x_next
        
        self.iteration_count += 1
        
        return x_next
    
    def iterate(self, n, discard=0):
        """
        N adım iterasyon yap
        
        Args:
        n : İterasyon sayısı
        discard : İlk kaç değeri atmak istiyoruz (transient effect)
        
        Returns:
        tuple: (x_sequence, normalized_sequence)
        """
        # İlk discard kadar değeri at (geçici etkileri temizle)
        for _ in range(discard):
            self.step()
        
        # Gerçek değerleri topla
        x_sequence = np.zeros(n)
        
        for i in range(n):
            x_sequence[i] = self.step()
        
        return x_sequence, x_sequence
    
    def get_key_stream(self, length, bits=8, skip_transient=False):
        """
        Şifreleme için anahtar akışı üret
        
        Args:
        length : Kaç byte anahtar gerekli
        bits : Her değer kaç bit (varsayılan 8)
        skip_transient : İlk 1000 adımı atla (varsayılan: False)
        
        Returns:
        numpy.ndarray: Uint8 anahtar akışı
        """
        # Transient'ı sadece istenirse at (UYARI: Her çağrıda atmak deşifrelemeyi bozar!)
        if skip_transient:
            for _ in range(1000):
                self.step()
        
        # Anahtar akışı üret
        key_stream = np.zeros(length, dtype=np.uint8)
        
        for i in range(length):
            # [0, 1] değerini [0, 255] aralığına dönüştür
            val = self.step()
            key_stream[i] = int(val * (2**bits - 1)) % (2**bits)
        
        return key_stream
    
    def lyapunov_exponent(self, n_iterations=10000, n_discard=1000):
        """
        Lyapunov üssünü hesapla
        Pozitif değer = kaotik, negatif = düzenli
        
        Returns:
        float: Lyapunov üssü (λ)
        """
        # Transient'ı at
        for _ in range(n_discard):
            self.step()
        
        lyap_sum = 0.0
        
        for _ in range(n_iterations):
            x = self.x_curr
            
            # df/dx hesapla (analitik türev)
            # f(x) = r*x*(1-x) + a*sin(πx) + b*x_{n-1}*sin(πx) + ...
            # df/dx ≈ r(1-2x) + πa*cos(πx) + πb*x_{n-1}*cos(πx) + ...
            
            df_dx = (self.r * (1 - 2*x) + 
                     np.pi * self.a * np.cos(np.pi * x) +
                     np.pi * self.b * self.x_prev * np.cos(np.pi * x) +
                     2 * np.pi * self.c * np.cos(2*np.pi*x) * np.cos(np.pi*self.x_prev))
            
            # Log türevlerini topla
            if abs(df_dx) > 1e-10:  # Sıfıra bölmeyi önle
                lyap_sum += np.log(abs(df_dx))
            
            self.step()
        
        lyapunov = lyap_sum / n_iterations
        
        return lyapunov
    
    def reset(self, x0=None, u0=None):
        """Sistemi başlangıç durumuna getir"""
        if x0 is not None:
            self.x_prev = x0 % 1.0
        if u0 is not None:
            self.x_curr = u0 % 1.0
        self.iteration_count = 0
    
    def __repr__(self):
        return (f"FPLM(x_prev={self.x_prev:.6f}, x_curr={self.x_curr:.6f}, "
                f"r={self.r}, iterations={self.iteration_count})")


if __name__ == "__main__":
    # Test kodu
    print("="*60)
    print("FPLM (Feedback Perturbation Logistic Map) Test")
    print("="*60)
    
    # FPLM oluştur
    fplm = FPLM(x0=0.5, u0=0.3, r=3.99, a=0.2, b=0.3, c=0.4, delta=0.1)
    
    # Lyapunov üssünü hesapla
    lyap = fplm.lyapunov_exponent()
    print(f"\nLyapunov Üssü (λ): {lyap:.6f}")
    
    if lyap > 0:
        print("✅ Sistem KAOTİK (λ > 0)")
    else:
        print("❌ Sistem düzenli (λ ≤ 0)")
    
    # Örnek dizi üret
    fplm.reset(x0=0.5, u0=0.3)
    sequence, _ = fplm.iterate(10, discard=100)
    
    print(f"\nİlk 10 değer (100 transient atıldıktan sonra):")
    for i, val in enumerate(sequence):
        print(f"  x[{i}] = {val:.8f}")
    
    # Anahtar akışı testi
    fplm.reset(x0=0.5, u0=0.3)
    key_stream = fplm.get_key_stream(16)
    print(f"\n16-byte anahtar akışı:")
    print(f"  {' '.join([f'{k:02X}' for k in key_stream])}")
    
    print("\n" + "="*60)
