"""
Kuantum Simülasyon Modülü
Qiskit ile kuantum kriptografi simülasyonları

Özellikler:
1. Kuantum Rastgele Sayı Üreteci (QRNG)
2. BB84 Kuantum Anahtar Dağıtımı
3. Qubit Süperpozisyon Gösterimi
4. Grover Algoritması Simülasyonu (Güvenlik Testi)
"""

import numpy as np

# Qiskit import - opsiyonel
try:
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    from qiskit.visualization import plot_histogram
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("⚠️  Qiskit bulunamadı - basit simülasyon modu kullanılacak")


class QuantumSimulator:
    """Kuantum kriptografi simülatörü"""
    
    def __init__(self):
        self.use_qiskit = QISKIT_AVAILABLE
        
    def generate_quantum_random_key(self, length=7):
        """
        Kuantum Rastgele Sayı Üreteci (QRNG)
        
        Süperpozisyon ve ölçüm belirsizliğini kullanarak
        gerçekten rastgele sayılar üretir.
        
        Args:
            length: Üretilecek sayı adedi
            
        Returns:
            list: Kuantum rastgele anahtar [x0, u0, r, a, b, c, delta]
        """
        if self.use_qiskit:
            return self._qiskit_random_key(length)
        else:
            return self._fallback_random_key(length)
    
    def _qiskit_random_key(self, length):
        """Qiskit ile gerçek kuantum simülasyonu"""
        key = []
        
        for i in range(length):
            # Her parametre için ayrı kuantum devresi
            qc = QuantumCircuit(8)  # 8 qubit = 256 olası durum
            
            # Süperpozisyon oluştur (Hadamard gate)
            for q in range(8):
                qc.h(q)
            
            # Ölç
            qc.measure_all()
            
            # Simüle et
            sampler = StatevectorSampler()
            result = sampler.run([qc], shots=1).result()
            
            # Sonucu al (8-bit sayı)
            counts = result[0].data.meas.get_counts()
            bitstring = list(counts.keys())[0]
            value = int(bitstring, 2) / 255.0  # [0, 1] normalize
            
            # Parametre aralıklarına uydur
            if i == 0 or i == 1:  # x0, u0
                key.append(value * 0.8 + 0.1)  # [0.1, 0.9]
            elif i == 2:  # r
                key.append(value * 0.3 + 3.7)  # [3.7, 4.0]
            else:  # a, b, c, delta
                if i < 6:
                    key.append(value * 0.4 + 0.1)  # [0.1, 0.5]
                else:
                    key.append(value * 0.15 + 0.05)  # [0.05, 0.2]
        
        return key
    
    def _fallback_random_key(self, length):
        """Qiskit yoksa klasik RNG (yine de güvenli)"""
        import random
        key = []
        
        for i in range(length):
            if i == 0 or i == 1:
                key.append(random.uniform(0.1, 0.9))
            elif i == 2:
                key.append(random.uniform(3.7, 4.0))
            else:
                if i < 6:
                    key.append(random.uniform(0.1, 0.5))
                else:
                    key.append(random.uniform(0.05, 0.2))
        
        return key
    
    def bb84_simulation(self, key_length=16):
        """
        BB84 Kuantum Anahtar Dağıtım Protokolü Simülasyonu
        
        Alice ve Bob arasında güvenli anahtar paylaşımı.
        Eve (dinleyici) tespit edilir.
        
        Returns:
            dict: Simülasyon sonuçları
        """
        if not self.use_qiskit:
            return self._fallback_bb84(key_length)
        
        # Alice'in rastgele bit dizisi
        alice_bits = [np.random.randint(0, 2) for _ in range(key_length)]
        # Alice'in basis seçimi (0: Z-basis, 1: X-basis)
        alice_bases = [np.random.randint(0, 2) for _ in range(key_length)]
        
        # Bob'un basis seçimi
        bob_bases = [np.random.randint(0, 2) for _ in range(key_length)]
        
        # Kuantum iletişim simülasyonu
        bob_measurements = []
        
        for i in range(key_length):
            qc = QuantumCircuit(1, 1)
            
            # Alice biti kodlar
            if alice_bits[i] == 1:
                qc.x(0)
            
            # Alice basis uygular
            if alice_bases[i] == 1:  # X-basis
                qc.h(0)
            
            # Bob basis uygular (ölçümden önce)
            if bob_bases[i] == 1:  # X-basis
                qc.h(0)
            
            # Bob ölçer
            qc.measure(0, 0)
            
            # Simüle et
            sampler = StatevectorSampler()
            result = sampler.run([qc], shots=1).result()
            counts = result[0].data.c.get_counts()
            measured = int(list(counts.keys())[0])
            
            bob_measurements.append(measured)
        
        # Basis karşılaştırması
        matching_bases = [i for i in range(key_length) if alice_bases[i] == bob_bases[i]]
        
        # Ortak anahtar
        shared_key = [alice_bits[i] for i in matching_bases]
        bob_key = [bob_measurements[i] for i in matching_bases]
        
        # Hata kontrolü (dinleme tespiti)
        errors = sum([1 for i in range(len(shared_key)) if shared_key[i] != bob_key[i]])
        error_rate = errors / len(shared_key) if len(shared_key) > 0 else 0
        
        return {
            'key_length': key_length,
            'matching_bases': len(matching_bases),
            'shared_key_length': len(shared_key),
            'error_rate': error_rate,
            'secure': error_rate < 0.11,  # %11'den az hata güvenli
            'alice_bits': alice_bits,
            'bob_measurements': bob_measurements,
            'final_key': shared_key[:8] if len(shared_key) >= 8 else shared_key
        }
    
    def _fallback_bb84(self, key_length):
        """Qiskit olmadan BB84 simülasyonu"""
        alice_bits = [np.random.randint(0, 2) for _ in range(key_length)]
        alice_bases = [np.random.randint(0, 2) for _ in range(key_length)]
        bob_bases = [np.random.randint(0, 2) for _ in range(key_length)]
        
        # Basis eşleşmesi
        matching = [i for i in range(key_length) if alice_bases[i] == bob_bases[i]]
        shared_key = [alice_bits[i] for i in matching]
        
        return {
            'key_length': key_length,
            'matching_bases': len(matching),
            'shared_key_length': len(shared_key),
            'error_rate': 0.0,  # İdeal durum
            'secure': True,
            'alice_bits': alice_bits,
            'bob_measurements': [alice_bits[i] if alice_bases[i] == bob_bases[i] else 1-alice_bits[i] for i in range(key_length)],
            'final_key': shared_key[:8] if len(shared_key) >= 8 else shared_key
        }
    
    def grover_security_test(self, encrypted_image, target_pattern_size=8):
        """
        Grover Algoritması ile Güvenlik Testi
        
        Kuantum bilgisayarın şifreli görüntüde pattern arama hızını simüle eder.
        Klasik arama: O(N), Grover: O(√N)
        
        Args:
            encrypted_image: Şifreli görüntü array'i
            target_pattern_size: Aranacak pattern boyutu
            
        Returns:
            dict: Güvenlik skoru ve analiz
        """
        if encrypted_image is None:
            return {'score': 0, 'message': 'Görüntü yok'}
        
        # Entropi hesapla
        hist = np.histogram(encrypted_image.flatten(), bins=256, range=(0, 256))[0]
        hist = hist / hist.sum()
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        
        # Pattern analizi (tekrar eden bloklar)
        H, W = encrypted_image.shape
        patterns = {}
        block_size = target_pattern_size
        
        for i in range(0, H - block_size, block_size):
            for j in range(0, W - block_size, block_size):
                block = encrypted_image[i:i+block_size, j:j+block_size]
                block_hash = hash(block.tobytes())
                patterns[block_hash] = patterns.get(block_hash, 0) + 1
        
        # Tekrar oranı
        total_blocks = len(patterns)
        unique_blocks = len(set(patterns.values()))
        uniqueness = unique_blocks / total_blocks if total_blocks > 0 else 1.0
        
        # Grover advantage hesapla
        classical_complexity = H * W
        quantum_complexity = np.sqrt(H * W)
        grover_advantage = classical_complexity / quantum_complexity
        
        # Güvenlik skoru (0-100)
        entropy_score = (entropy / 8.0) * 40  # Maks 40 puan
        uniqueness_score = uniqueness * 30    # Maks 30 puan
        grover_resistance = min(30, (grover_advantage / 100) * 30)  # Maks 30 puan
        
        total_score = entropy_score + uniqueness_score + grover_resistance
        
        return {
            'score': round(total_score, 2),
            'entropy': round(entropy, 4),
            'uniqueness': round(uniqueness, 4),
            'grover_advantage': round(grover_advantage, 2),
            'classical_time': classical_complexity,
            'quantum_time': round(quantum_complexity, 2),
            'secure': total_score > 85,
            'message': self._get_security_message(total_score)
        }
    
    def _get_security_message(self, score):
        """Güvenlik skoru mesajı"""
        if score >= 95:
            return "🔒 Mükemmel! Kuantum saldırılara karşı çok güvenli."
        elif score >= 85:
            return "✅ İyi! Kuantum bilgisayarlar için yeterince güvenli."
        elif score >= 70:
            return "⚠️ Orta! Bazı iyileştirmeler gerekebilir."
        else:
            return "❌ Zayıf! Güvenlik açıkları mevcut."
    
    def create_bell_state(self):
        """
        Bell State (Kuantum Dolaşıklık) Oluştur
        
        İki qubit'i dolaştırır - klasik fizikle açıklanamayan bir durum.
        """
        if not self.use_qiskit:
            return None
        
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        
        sampler = StatevectorSampler()
        result = sampler.run([qc], shots=1024).result()
        counts = result[0].data.meas.get_counts()
        
        return {
            'circuit': qc,
            'counts': counts,
            'description': 'Bell State: |00⟩ ve |11⟩ süperpozisyonu'
        }


if __name__ == "__main__":
    # Test
    print("="*60)
    print("KUANTUM SİMÜLATÖR TESTİ")
    print("="*60)
    
    sim = QuantumSimulator()
    
    # QRNG testi
    print("\n[1] Kuantum Rastgele Anahtar Üretimi:")
    key = sim.generate_quantum_random_key()
    print(f"Anahtar: {[round(x, 4) for x in key]}")
    
    # BB84 testi
    print("\n[2] BB84 Kuantum Anahtar Dağıtımı:")
    bb84_result = sim.bb84_simulation(16)
    print(f"Ortak anahtar uzunluğu: {bb84_result['shared_key_length']}")
    print(f"Hata oranı: {bb84_result['error_rate']:.2%}")
    print(f"Güvenli: {'✅' if bb84_result['secure'] else '❌'}")
    
    # Güvenlik testi
    print("\n[3] Grover Güvenlik Testi:")
    test_img = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
    security = sim.grover_security_test(test_img)
    print(f"Güvenlik skoru: {security['score']}/100")
    print(f"Entropi: {security['entropy']}")
    print(f"Mesaj: {security['message']}")
    
    print("\n" + "="*60)
