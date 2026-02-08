"""
Toroidal DFS - Toroidal (Simit Yüzeyli) Graf üzerinde Anahtar Bağımlı DFS

Bu modül, görüntüyü düzlemsel ızgara yerine toroidal (simit) yüzeyli bir graf
olarak modeller. Bu yapıda kenar piksellerinin de 4 komşusu vardır (kenar etkisi yok).

Rapordaki Bölüm 4.2'yi uygular.
"""

import numpy as np
from fplm import FPLM


class ToroidalDFS:
    """
    Toroidal Graf üzerinde Anahtar-Bağımlı Depth First Search
    
    Toroidal yapı: Sağ kenar → Sol kenar, Alt kenar → Üst kenar bağlıdır
    Her düğümün derecesi (degree) tam olarak 4'tür.
    """
    
    def __init__(self, height, width, fplm):
        """
        Args:
        height : Görüntü yüksekliği
        width : Görüntü genişliği
        fplm : FPLM nesnesi (gezinti yönünü belirler)
        """
        self.H = height
        self.W = width
        self.fplm = fplm
        
        # Ziyaret edilme durumları
        self.visited = np.zeros((height, width), dtype=bool)
        
        # Gezinti yolu
        self.path = []
    
    def get_neighbors(self, row, col):
        """
        Toroidal yapıda (row, col) düğümünün 4 komşusunu döndür
        
        Toroidal bağlantı:
        - Sağa giderken: (row, col+1) → (row, (col+1) % W)
        - Sola giderken: (row, col-1) → (row, (col-1) % W)
        - Aşağı: ((row+1) % H, col)
        - Yukarı: ((row-1) % H, col)
        
        Returns:
        list: 4 komşu [(r1,c1), (r2,c2), (r3,c3), (r4,c4)]
        """
        neighbors = [
            ((row - 1) % self.H, col),        # Yukarı (UP)
            ((row + 1) % self.H, col),        # Aşağı (DOWN)
            (row, (col - 1) % self.W),        # Sol (LEFT)
            (row, (col + 1) % self.W)         # Sağ (RIGHT)
        ]
        
        return neighbors
    
    def shuffle_neighbors(self, neighbors):
        """
        Komşuları FPLM'den gelen kaotik sayıya göre karıştır
        Bu, her şifrelemede farklı bir gezinti yolu oluşturur
        
        Args:
        neighbors : Komşu listesi
        
        Returns:
        list: Karıştırılmış komşu listesi
        """
        # FPLM'den rastgele sayı al
        rand_val = self.fplm.step()
        
        # [0, 1] değerini [0, 23] aralığına çevir (4! = 24 permütasyon)
        perm_index = int(rand_val * 24) % 24
        
        # 24 olası permütasyondan birini seç
        permutations = [
            [0, 1, 2, 3], [0, 1, 3, 2], [0, 2, 1, 3], [0, 2, 3, 1],
            [0, 3, 1, 2], [0, 3, 2, 1], [1, 0, 2, 3], [1, 0, 3, 2],
            [1, 2, 0, 3], [1, 2, 3, 0], [1, 3, 0, 2], [1, 3, 2, 0],
            [2, 0, 1, 3], [2, 0, 3, 1], [2, 1, 0, 3], [2, 1, 3, 0],
            [2, 3, 0, 1], [2, 3, 1, 0], [3, 0, 1, 2], [3, 0, 2, 1],
            [3, 1, 0, 2], [3, 1, 2, 0], [3, 2, 0, 1], [3, 2, 1, 0]
        ]
        
        perm = permutations[perm_index]
        shuffled = [neighbors[i] for i in perm]
        
        return shuffled
    
    def dfs(self, row, col):
        """
        Iterative Depth First Search (Stack kullanarak)
        
        Args:
        row, col : Başlangıç noktası
        """
        # Stack kullanarak iterative DFS
        stack = [(row, col)]
        
        while stack:
            curr_row, curr_col = stack.pop()
            
            # Zaten ziyaret edildiyse atla
            if self.visited[curr_row, curr_col]:
                continue
            
            # Bu düğümü ziyaret et
            self.visited[curr_row, curr_col] = True
            self.path.append((curr_row, curr_col))
            
            # Komşuları al ve FPLM ile karıştır
            neighbors = self.get_neighbors(curr_row, curr_col)
            shuffled_neighbors = self.shuffle_neighbors(neighbors)
            
            # Komşuları stack'e ekle (ziyaret edilmemişlerse)
            for (r, c) in reversed(shuffled_neighbors):  # Ters sırada ekle (DFS sırası için)
                if not self.visited[r, c]:
                    stack.append((r, c))
    
    def generate_path(self):
        """
        Toroidal graf üzerinde tam bir gezinti yolu oluştur
        
        Returns:
        list: [(r1,c1), (r2,c2), ...] şeklinde gezinti yolu
        """
        # Her şeyi sıfırla
        self.visited.fill(False)
        self.path = []
        
        # FPLM'den başlangıç noktası belirle
        start_val = self.fplm.step()
        start_row = int(start_val * self.H) % self.H
        start_col = int((start_val * 1000) * self.W) % self.W  # Farklı bir seed
        
        # DFS'yi başlat
        self.dfs(start_row, start_col)
        
        # Eğer tüm düğümler ziyaret edilmediyse (bağlantısız bileşenler varsa)
        # kalan düğümleri de ziyaret et
        for r in range(self.H):
            for c in range(self.W):
                if not self.visited[r, c]:
                    self.dfs(r, c)
        
        return self.path
    
    def visualize_path(self, save_path=None):
        """
        Gezinti yolunu görselleştir
        
        Args:
        save_path : Kayıt yolu (opsiyonel)
        """
        import matplotlib.pyplot as plt
        
        # Yolu matrise dönüştür (ziyaret sırası)
        order_matrix = np.zeros((self.H, self.W), dtype=int)
        
        for idx, (r, c) in enumerate(self.path):
            order_matrix[r, c] = idx
        
        # Görselleştirme
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Sol: Toroidal bağlantılar
        ax1.set_title("Toroidal Graf Yapısı\n(Kenarlar Birbirine Bağlı)", 
                     fontsize=14, fontweight='bold')
        ax1.set_xlim(-0.5, self.W - 0.5)
        ax1.set_ylim(self.H - 0.5, -0.5)
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        
        # Grid çiz
        for i in range(self.H):
            for j in range(self.W):
                ax1.plot(j, i, 'o', color='blue', markersize=3)
        
        # Toroidal bağlantıları göster (kenar pikselleri)
        # Üst-alt bağlantısı (kırmızı)
        for j in range(0, self.W, max(1, self.W//10)):
            ax1.plot([j, j], [0, self.H-1], 'r--', alpha=0.5, linewidth=2)
        
        # Sol-sağ bağlantısı (yeşil)
        for i in range(0, self.H, max(1, self.H//10)):
            ax1.plot([0, self.W-1], [i, i], 'g--', alpha=0.5, linewidth=2)
        
        ax1.text(self.W/2, -1, "Üst ↔ Alt Bağlantısı", 
                ha='center', color='red', fontsize=10)
        ax1.text(-1, self.H/2, "Sol ↔ Sağ\nBağlantısı", 
                va='center', ha='right', color='green', fontsize=10)
        
        # Sağ: DFS yolu
        ax2.set_title("Kaotik DFS Gezinti Yolu\n(FPLM Anahtarıyla Oluşturuldu)", 
                     fontsize=14, fontweight='bold')
        
        # Gezinti heatmap'i
        im = ax2.imshow(order_matrix, cmap='hot', interpolation='nearest')
        plt.colorbar(im, ax=ax2, label='Ziyaret Sırası')
        
        # İlk birkaç adımı göster (ok ile)
        num_arrows = min(50, len(self.path) - 1)
        for i in range(num_arrows):
            r1, c1 = self.path[i]
            r2, c2 = self.path[i+1]
            
            # Toroidal wrap'i hesaba kat
            dc = c2 - c1
            dr = r2 - r1
            
            if abs(dc) > self.W / 2:
                dc = -(np.sign(dc) * (self.W - abs(dc)))
            if abs(dr) > self.H / 2:
                dr = -(np.sign(dr) * (self.H - abs(dr)))
            
            ax2.arrow(c1, r1, dc*0.7, dr*0.7, 
                     head_width=0.3, head_length=0.2, 
                     fc='cyan', ec='cyan', alpha=0.6, linewidth=1)
        
        ax2.set_xlabel('Sütun (Column)')
        ax2.set_ylabel('Satır (Row)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Görsel kaydedildi: {save_path}")
        
        plt.show()
    
    def __repr__(self):
        return f"ToroidalDFS({self.H}x{self.W}, visited={np.sum(self.visited)}/{self.H*self.W})"


if __name__ == "__main__":
    # Test kodu
    print("="*60)
    print("Toroidal DFS Test")
    print("="*60)
    
    # FPLM oluştur
    fplm = FPLM(x0=0.7, u0=0.4, r=3.99)
    
    # Küçük bir grid (8x8) üzerinde test
    tdfs = ToroidalDFS(8, 8, fplm)
    
    # Gezinti yolu oluştur
    path = tdfs.generate_path()
    
    print(f"\nGrid boyutu: {tdfs.H}x{tdfs.W} = {tdfs.H * tdfs.W} piksel")
    print(f"Üretilen yol uzunluğu: {len(path)}")
    print(f"Tüm pikseller ziyaret edildi mi? {len(path) == tdfs.H * tdfs.W}")
    
    # İlk 10 adımı göster
    print(f"\nİlk 10 adım:")
    for i in range(min(10, len(path))):
        r, c = path[i]
        print(f"  Adım {i}: ({r}, {c})")
    
    # Bir piksel örneği al ve komşularını göster
    test_row, test_col = 0, 0
    neighbors = tdfs.get_neighbors(test_row, test_col)
    print(f"\n({test_row}, {test_col}) pikselinin toroidal komşuları:")
    for i, (r, c) in enumerate(neighbors):
        direction = ['Yukarı', 'Aşağı', 'Sol', 'Sağ'][i]
        print(f"  {direction}: ({r}, {c})")
    
    # Görselleştir
    print("\nGörselleştirme oluşturuluyor...")
    tdfs.visualize_path("toroidal_dfs_visualization.png")
    
    print("\n" + "="*60)
