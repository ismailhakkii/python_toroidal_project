"""
ChaosPolybius-2026 GUI
Tkinter ile Modern Görsel Arayüz

Özellikler:
- Görüntü yükleme ve önizleme
- Şifreleme/Deşifreleme
- Gerçek zamanlı güvenlik metrikleri
- Sonuç görselleştirme
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
from encryption import encrypt_image, decrypt_image, encrypt_image_from_array
from security_metrics import SecurityMetrics
from quantum_simulator import QuantumSimulator


class ChaosPolybiusGUI:
    """Ana GUI Sınıfı"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ChaosPolybius-2026 - Kaotik Görüntü Şifreleme Sistemi")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e2e')
        
        # Stil ayarları
        self.setup_styles()
        
        # Değişkenler
        self.original_image = None
        self.encrypted_image = None
        self.decrypted_image = None
        self.original_path = None
        self.base_key = [0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1]
        
        # Kuantum simülatör
        self.quantum_sim = QuantumSimulator()
        
        # Ana layout
        self.create_widgets()
        
    def setup_styles(self):
        """Tema ve stil ayarları"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Renkler
        bg_dark = '#1e1e2e'
        bg_medium = '#2d2d44'
        fg_light = '#ffffff'
        accent = '#7aa2f7'
        success = '#9ece6a'
        warning = '#e0af68'
        
        style.configure('Title.TLabel', 
                       background=bg_dark, 
                       foreground=accent,
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background=bg_dark, 
                       foreground=fg_light,
                       font=('Segoe UI', 10))
        
        style.configure('Custom.TButton',
                       background=accent,
                       foreground=fg_light,
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Custom.TFrame',
                       background=bg_dark)
        
        style.configure('Panel.TFrame',
                       background=bg_medium,
                       relief='ridge',
                       borderwidth=1)
        
    def create_widgets(self):
        """Widget'ları oluştur"""
        
        # Başlık
        header_frame = ttk.Frame(self.root, style='Custom.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(header_frame, 
                               text="🔐 ChaosPolybius-2026", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame,
                                   text="Geri Beslemeli Pertürbasyon ve Toroidal Graf ile Görüntü Şifreleme",
                                   style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # Notebook (Tab yapısı)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Şifreleme
        encryption_tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(encryption_tab, text="🔒 Şifreleme")
        self.create_encryption_tab(encryption_tab)
        
        # Tab 2: Kuantum Simülasyonu
        quantum_tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(quantum_tab, text="🔬 Kuantum Simülasyonu")
        self.create_quantum_tab(quantum_tab)
        
        # Alt panel - Log
        bottom_panel = ttk.Frame(self.root, style='Panel.TFrame')
        bottom_panel.pack(fill=tk.X, padx=10, pady=5)
        
        self.create_log_panel(bottom_panel)
    
    def create_encryption_tab(self, parent):
        """Şifreleme sekmesi"""
        # Ana container
        main_container = ttk.Frame(parent, style='Custom.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sol panel - Kontroller
        left_panel = ttk.Frame(main_container, style='Panel.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.create_control_panel(left_panel)
        
        # Sağ panel - Görüntüler
        right_panel = ttk.Frame(main_container, style='Custom.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_image_panel(right_panel)
        
    def create_control_panel(self, parent):
        """Kontrol paneli"""
        # Dosya işlemleri
        file_frame = ttk.LabelFrame(parent, text="📁 Dosya İşlemleri", 
                                    style='Custom.TFrame')
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(file_frame, text="Görüntü Yükle",
                  command=self.load_image,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Şifreli Görüntü Kaydet",
                  command=self.save_encrypted,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Sonuçları Dışa Aktar",
                  command=self.export_results,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        # Anahtar ayarları
        key_frame = ttk.LabelFrame(parent, text="🔑 Anahtar Parametreleri",
                                   style='Custom.TFrame')
        key_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.key_entries = []
        key_labels = ['x0', 'u0', 'r', 'a', 'b', 'c', 'δ']
        
        for i, (label, value) in enumerate(zip(key_labels, self.base_key)):
            frame = ttk.Frame(key_frame, style='Custom.TFrame')
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"{label}:", 
                     background='#2d2d44', 
                     foreground='#ffffff',
                     width=4).pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame, width=12)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=5)
            self.key_entries.append(entry)
        
        ttk.Button(key_frame, text="Anahtarı Güncelle",
                  command=self.update_key,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(key_frame, text="Rastgele Anahtar",
                  command=self.generate_random_key,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        # Şifreleme işlemleri
        encrypt_frame = ttk.LabelFrame(parent, text="⚙️ Şifreleme",
                                      style='Custom.TFrame')
        encrypt_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(encrypt_frame, text="🔒 ŞİFRELE",
                  command=self.encrypt_image_thread,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(encrypt_frame, text="🔓 DEŞİFRELE",
                  command=self.decrypt_image_thread,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(encrypt_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Güvenlik metrikleri
        metrics_frame = ttk.LabelFrame(parent, text="📊 Güvenlik Metrikleri",
                                      style='Custom.TFrame')
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame,
                                                      height=12,
                                                      width=30,
                                                      bg='#1e1e2e',
                                                      fg='#ffffff',
                                                      font=('Consolas', 9))
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(metrics_frame, text="Metrikleri Hesapla",
                  command=self.calculate_metrics,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
    def create_image_panel(self, parent):
        """Görüntü gösterim paneli"""
        # Üst frame - Orijinal ve Şifreli
        top_frame = ttk.Frame(parent, style='Custom.TFrame')
        top_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Orijinal görüntü
        orig_frame = ttk.LabelFrame(top_frame, text="📷 Orijinal Görüntü",
                                   style='Custom.TFrame')
        orig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_canvas = tk.Canvas(orig_frame, bg='#2d2d44', 
                                        width=280, height=280)
        self.original_canvas.pack(padx=5, pady=5)
        
        # Şifreli görüntü
        enc_frame = ttk.LabelFrame(top_frame, text="🔒 Şifreli Görüntü",
                                  style='Custom.TFrame')
        enc_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.encrypted_canvas = tk.Canvas(enc_frame, bg='#2d2d44',
                                         width=280, height=280)
        self.encrypted_canvas.pack(padx=5, pady=5)
        
        # Alt frame - Deşifreli ve Histogram
        bottom_frame = ttk.Frame(parent, style='Custom.TFrame')
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Deşifreli görüntü
        dec_frame = ttk.LabelFrame(bottom_frame, text="🔓 Deşifreli Görüntü",
                                  style='Custom.TFrame')
        dec_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.decrypted_canvas = tk.Canvas(dec_frame, bg='#2d2d44',
                                         width=280, height=280)
        self.decrypted_canvas.pack(padx=5, pady=5)
        
        # Histogram
        hist_frame = ttk.LabelFrame(bottom_frame, text="📈 Histogram",
                                   style='Custom.TFrame')
        hist_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.histogram_canvas = tk.Canvas(hist_frame, bg='#2d2d44',
                                         width=280, height=280)
        self.histogram_canvas.pack(padx=5, pady=5)
        
    def create_log_panel(self, parent):
        """Log/konsol paneli"""
        log_label = ttk.Label(parent, text="📝 İşlem Günlüğü",
                             background='#2d2d44',
                             foreground='#ffffff',
                             font=('Segoe UI', 10, 'bold'))
        log_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.log_text = scrolledtext.ScrolledText(parent,
                                                  height=8,
                                                  bg='#1e1e2e',
                                                  fg='#9ece6a',
                                                  font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log("✅ Sistem hazır. Görüntü yükleyin veya parametreleri ayarlayın.")
        
    def log(self, message):
        """Log mesajı ekle"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def load_image(self):
        """Görüntü yükle"""
        filepath = filedialog.askopenfilename(
            title="Görüntü Seç",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), 
                      ("Tüm Dosyalar", "*.*")]
        )
        
        if filepath:
            self.original_path = filepath
            self.original_image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            
            if self.original_image is None:
                messagebox.showerror("Hata", "Görüntü yüklenemedi!")
                return
            
            self.log(f"✅ Görüntü yüklendi: {filepath.split('/')[-1]}")
            self.log(f"   Boyut: {self.original_image.shape}")
            
            self.display_image(self.original_image, self.original_canvas)
            
    def display_image(self, img, canvas):
        """Görüntüyü canvas'a çiz"""
        if img is None:
            return
        
        # Görüntüyü yeniden boyutlandır
        h, w = img.shape
        canvas_w = canvas.winfo_width() if canvas.winfo_width() > 1 else 280
        canvas_h = canvas.winfo_height() if canvas.winfo_height() > 1 else 280
        
        scale = min(canvas_w / w, canvas_h / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(img, (new_w, new_h))
        
        # PIL'e çevir
        pil_img = Image.fromarray(resized)
        photo = ImageTk.PhotoImage(pil_img)
        
        # Canvas'a çiz
        canvas.delete("all")
        canvas.create_image(canvas_w//2, canvas_h//2, image=photo)
        canvas.image = photo  # Referansı tut
        
    def update_key(self):
        """Anahtar parametrelerini güncelle"""
        try:
            self.base_key = [float(entry.get()) for entry in self.key_entries]
            self.log("✅ Anahtar parametreleri güncellendi")
            self.log(f"   Yeni anahtar: {self.base_key}")
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz parametre değeri!")
            
    def generate_random_key(self):
        """Rastgele anahtar üret"""
        import random
        self.base_key = [
            random.uniform(0.1, 0.9),  # x0
            random.uniform(0.1, 0.9),  # u0
            random.uniform(3.7, 4.0),  # r
            random.uniform(0.1, 0.5),  # a
            random.uniform(0.1, 0.5),  # b
            random.uniform(0.1, 0.5),  # c
            random.uniform(0.05, 0.2)  # delta
        ]
        
        for entry, value in zip(self.key_entries, self.base_key):
            entry.delete(0, tk.END)
            entry.insert(0, f"{value:.4f}")
        
        self.log("🎲 Rastgele anahtar oluşturuldu")
        
    def encrypt_image_thread(self):
        """Şifreleme işlemini thread'de çalıştır"""
        if self.original_image is None:
            messagebox.showwarning("Uyarı", "Önce bir görüntü yükleyin!")
            return
        
        self.update_key()
        
        thread = threading.Thread(target=self._encrypt_image)
        thread.daemon = True
        thread.start()
        
    def _encrypt_image(self):
        """Şifreleme işlemi"""
        self.progress.start()
        self.log("🔒 Şifreleme başlıyor...")
        
        try:
            start = time.time()
            
            # Direkt array'den şifrele (dosya kaydetmeye gerek yok)
            from encryption import encrypt_image_from_array
            self.encrypted_image = encrypt_image_from_array(self.original_image, self.base_key)
            
            elapsed = (time.time() - start) * 1000
            
            self.log(f"✅ Şifreleme tamamlandı ({elapsed:.1f} ms)")
            
            # Göster
            self.display_image(self.encrypted_image, self.encrypted_canvas)
            self.draw_histogram(self.encrypted_image)
            
        except Exception as e:
            self.log(f"❌ Hata: {str(e)}")
            messagebox.showerror("Hata", f"Şifreleme hatası: {str(e)}")
        finally:
            self.progress.stop()
            
    def decrypt_image_thread(self):
        """Deşifreleme işlemini thread'de çalıştır"""
        if self.encrypted_image is None:
            messagebox.showwarning("Uyarı", "Önce şifreleme yapın!")
            return
        
        thread = threading.Thread(target=self._decrypt_image)
        thread.daemon = True
        thread.start()
        
    def _decrypt_image(self):
        """Deşifreleme işlemi"""
        self.progress.start()
        self.log("🔓 Deşifreleme başlıyor...")
        
        try:
            start = time.time()
            
            self.decrypted_image = decrypt_image(
                self.encrypted_image, 
                self.base_key, 
                self.original_image
            )
            
            elapsed = (time.time() - start) * 1000
            
            # MSE hesapla
            mse = np.mean((self.original_image - self.decrypted_image) ** 2)
            
            self.log(f"✅ Deşifreleme tamamlandı ({elapsed:.1f} ms)")
            self.log(f"   MSE: {mse:.6f} {'✅' if mse == 0 else '❌'}")
            
            # Göster
            self.display_image(self.decrypted_image, self.decrypted_canvas)
            
        except Exception as e:
            self.log(f"❌ Hata: {str(e)}")
            messagebox.showerror("Hata", f"Deşifreleme hatası: {str(e)}")
        finally:
            self.progress.stop()
            
    def draw_histogram(self, img):
        """Histogram çiz"""
        if img is None:
            return
        
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist = hist.ravel()
        
        # Canvas boyutu
        w = 280
        h = 280
        
        # Normalize et
        max_val = np.max(hist)
        if max_val > 0:
            hist = (hist / max_val) * (h - 20)
        
        self.histogram_canvas.delete("all")
        
        # Çubuklar
        bar_width = w / 256
        for i, val in enumerate(hist):
            x = i * bar_width
            self.histogram_canvas.create_line(
                x, h, x, h - val,
                fill='#7aa2f7', width=bar_width
            )
        
    def calculate_metrics(self):
        """Güvenlik metriklerini hesapla"""
        if self.original_image is None or self.encrypted_image is None:
            messagebox.showwarning("Uyarı", "Önce şifreleme yapın!")
            return
        
        self.log("📊 Metrikler hesaplanıyor...")
        
        try:
            metrics = SecurityMetrics()
            
            # Entropi
            entropy_orig = metrics.entropy(self.original_image)
            entropy_enc = metrics.entropy(self.encrypted_image)
            
            # Korelasyon
            corr_enc_h = metrics.correlation(self.encrypted_image, 'horizontal')
            corr_enc_v = metrics.correlation(self.encrypted_image, 'vertical')
            
            # NPCR/UACI (1 piksel değiştir)
            modified = self.original_image.copy()
            modified[0, 0] = np.uint8((int(modified[0, 0]) + 1) % 256)
            
            enc1 = encrypt_image_from_array(self.original_image, self.base_key)
            enc2 = encrypt_image_from_array(modified, self.base_key)
            
            npcr = metrics.npcr(enc1, enc2)
            uaci = metrics.uaci(enc1, enc2)
            
            # Göster
            self.metrics_text.delete(1.0, tk.END)
            
            result = f"""
╔══════════════════════════════╗
║   GÜVENLİK METRİKLERİ        ║
╚══════════════════════════════╝

📈 ENTROPİ
  Orijinal:  {entropy_orig:.4f} bit
  Şifreli:   {entropy_enc:.4f} bit
  Hedef:     8.0000 bit
  Durum:     {'✅' if entropy_enc > 7.99 else '❌'}

📊 KORELASYON
  Yatay:     {corr_enc_h:.6f}
  Dikey:     {corr_enc_v:.6f}
  Hedef:     0.0000
  Durum:     {'✅' if abs(corr_enc_h) < 0.01 else '⚠️'}

🔬 DİFERANSİYEL ANALİZ
  NPCR:      {npcr:.4f}%
  Hedef:     >99.60%
  Durum:     {'✅' if npcr > 99.60 else '⚠️'}
  
  UACI:      {uaci:.4f}%
  Hedef:     33.28-33.64%
  Durum:     {'✅' if 33.28 < uaci < 33.64 else '⚠️'}

{'='*30}
GENEL SONUÇ: {'✅ BAŞARILI' if (entropy_enc > 7.99 and abs(corr_enc_h) < 0.01) else '⚠️ İNCELE'}
"""
            
            self.metrics_text.insert(1.0, result)
            self.log("✅ Metrikler hesaplandı")
            
        except Exception as e:
            self.log(f"❌ Metrik hatası: {str(e)}")
            
    def save_encrypted(self):
        """Şifreli görüntüyü kaydet"""
        if self.encrypted_image is None:
            messagebox.showwarning("Uyarı", "Önce şifreleme yapın!")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Tüm Dosyalar", "*.*")]
        )
        
        if filepath:
            cv2.imwrite(filepath, self.encrypted_image)
            self.log(f"💾 Şifreli görüntü kaydedildi: {filepath.split('/')[-1]}")
    
    def create_quantum_tab(self, parent):
        """Kuantum simülasyon sekmesi"""
        # Ana container
        main_container = ttk.Frame(parent, style='Custom.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sol panel - Kontroller
        left_panel = ttk.Frame(main_container, style='Panel.TFrame', width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Başlık
        ttk.Label(left_panel, text="🔬 Kuantum Kriptografi",
                 font=('Segoe UI', 14, 'bold'),
                 foreground='#89b4fa',
                 background='#2d2d44').pack(pady=10)
        
        # QRNG - Kuantum Rastgele Anahtar
        qrng_frame = ttk.LabelFrame(left_panel, text="Kuantum Rastgele Anahtar Üreteci",
                                    style='Custom.TFrame')
        qrng_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(qrng_frame, text="Süperpozisyon ve ölçüm belirsizliği\nile gerçek rastgele anahtar üretir.",
                 style='Subtitle.TLabel',
                 wraplength=300).pack(pady=5)
        
        ttk.Button(qrng_frame, text="🎲 Kuantum Anahtar Üret",
                  command=self.generate_quantum_key,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        self.quantum_key_text = scrolledtext.ScrolledText(qrng_frame,
                                                          height=4,
                                                          width=40,
                                                          bg='#1e1e2e',
                                                          fg='#cdd6f4',
                                                          font=('Consolas', 9))
        self.quantum_key_text.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(qrng_frame, text="📋 Anahtarı Kullan",
                  command=self.use_quantum_key,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        # BB84 Simülasyonu
        bb84_frame = ttk.LabelFrame(left_panel, text="BB84 Kuantum Anahtar Dağıtımı",
                                   style='Custom.TFrame')
        bb84_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(bb84_frame, text="Alice ve Bob güvenli anahtar paylaşır.\nDinleme (Eve) tespit edilir.",
                 style='Subtitle.TLabel',
                 wraplength=300).pack(pady=5)
        
        ttk.Button(bb84_frame, text="🔐 BB84 Simülasyonu Çalıştır",
                  command=self.run_bb84_simulation,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        # Grover Güvenlik Testi
        grover_frame = ttk.LabelFrame(left_panel, text="Grover Güvenlik Testi",
                                     style='Custom.TFrame')
        grover_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(grover_frame, text="Kuantum bilgisayar saldırılarına\nkarşı güvenlik analizi.",
                 style='Subtitle.TLabel',
                 wraplength=300).pack(pady=5)
        
        ttk.Button(grover_frame, text="🛡️ Güvenlik Testi Yap",
                  command=self.run_grover_test,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        # Sağ panel - Sonuçlar
        right_panel = ttk.Frame(main_container, style='Custom.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(right_panel, text="📊 Kuantum Simülasyon Sonuçları",
                 font=('Segoe UI', 12, 'bold'),
                 foreground='#89b4fa',
                 background='#1e1e2e').pack(pady=10)
        
        self.quantum_results = scrolledtext.ScrolledText(right_panel,
                                                         height=30,
                                                         bg='#1e1e2e',
                                                         fg='#cdd6f4',
                                                         font=('Consolas', 10))
        self.quantum_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Başlangıç mesajı
        welcome_msg = """
╔══════════════════════════════════════════════════════════╗
║        🔬 KUANTUM KRİPTOGRAFİ SİMÜLATÖRÜ 🔬            ║
╚══════════════════════════════════════════════════════════╝

Bu modül, kuantum bilgisayar ve kuantum kriptografi
konseptlerini simüle eder.

📌 ÖZELLİKLER:

1. 🎲 Kuantum Rastgele Sayı Üreteci (QRNG)
   - Süperpozisyon prensibini kullanır
   - Gerçek rastgele anahtar üretir
   - Klasik RNG'den daha güvenli

2. 🔐 BB84 Protokolü
   - Kuantum anahtar dağıtım simülasyonu
   - Alice ↔ Bob güvenli iletişim
   - Dinleme tespit mekanizması

3. 🛡️ Grover Algoritması Güvenlik Testi
   - Kuantum arama algoritması simülasyonu
   - Şifreli görüntü güvenlik analizi
   - Post-quantum crypto değerlendirmesi

💡 NOT: Bu simülasyonlar eğitici amaçlıdır.
   Gerçek kuantum bilgisayar gerektirmez.

Başlamak için sol panelden bir işlem seçin!
"""
        self.quantum_results.insert('1.0', welcome_msg)
    
    def generate_quantum_key(self):
        """Kuantum rastgele anahtar üret"""
        self.quantum_results.delete('1.0', tk.END)
        self.quantum_results.insert('1.0', "🎲 Kuantum anahtar üretiliyor...\n\n")
        self.quantum_results.update()
        
        key = self.quantum_sim.generate_quantum_random_key(7)
        
        result = f"""
╔══════════════════════════════════════════════════════════╗
║           🎲 KUANTUM RASTGELE ANAHTAR ÜRETİCİ          ║
╚══════════════════════════════════════════════════════════╝

🔬 Metod: Süperpozisyon + Kuantum Ölçümü
📊 Qubit Sayısı: 8 qubit per parametre
🎯 Belirsizlik: Heisenberg İlkesi

🔑 ÜRETILEN ANAHTAR:

  x0    = {key[0]:.6f}  (İlk durum - FPLM)
  u0    = {key[1]:.6f}  (İkinci durum - FPLM)
  r     = {key[2]:.6f}  (Kaos parametresi)
  a     = {key[3]:.6f}  (Pertürbasyon 1)
  b     = {key[4]:.6f}  (Pertürbasyon 2)
  c     = {key[5]:.6f}  (Pertürbasyon 3)
  delta = {key[6]:.6f}  (Geri besleme oranı)

✨ Kuantum Özellikler:
  • Her ölçüm tamamen farklıdır (belirsizlik)
  • Klasik RNG'den daha rastgele
  • Tahmin edilemez (no-cloning teoremi)

💡 Bu anahtarı şifreleme için kullanabilirsiniz!
   "Anahtarı Kullan" butonuna basın.
"""
        
        self.quantum_results.insert(tk.END, result)
        self.quantum_key_text.delete('1.0', tk.END)
        self.quantum_key_text.insert('1.0', str([round(x, 6) for x in key]))
        
        self.current_quantum_key = key
        self.log(f"🎲 Kuantum anahtar üretildi")
    
    def use_quantum_key(self):
        """Üretilen kuantum anahtarı kullan"""
        if hasattr(self, 'current_quantum_key'):
            self.base_key = self.current_quantum_key
            
            # Anahtar entry'lerini güncelle
            for i, entry in enumerate(self.key_entries):
                entry.delete(0, tk.END)
                entry.insert(0, f"{self.base_key[i]:.6f}")
            
            self.log(f"✅ Kuantum anahtar aktif edildi")
            messagebox.showinfo("Başarılı", "Kuantum anahtar şifreleme için hazır!")
        else:
            messagebox.showwarning("Uyarı", "Önce bir kuantum anahtar üretin!")
    
    def run_bb84_simulation(self):
        """BB84 kuantum anahtar dağıtımı simülasyonu"""
        self.quantum_results.delete('1.0', tk.END)
        self.quantum_results.insert('1.0', "🔐 BB84 Protokolü simüle ediliyor...\n\n")
        self.quantum_results.update()
        
        result = self.quantum_sim.bb84_simulation(32)
        
        output = f"""
╔══════════════════════════════════════════════════════════╗
║         🔐 BB84 KUANTUM ANAHTAR DAĞITIMI               ║
╚══════════════════════════════════════════════════════════╝

👤 PROTOKOL ADIMLARI:

1. Alice {result['key_length']} qubit hazırlar
   └─ Rastgele bit + rastgele basis seçimi

2. Alice → Bob (kuantum kanal)
   └─ Qubitler gönderilir

3. Bob ölçüm yapar
   └─ Rastgele basis seçimi

4. Alice ↔ Bob basis karşılaştırması (klasik kanal)
   └─ Eşleşen bazlar: {result['matching_bases']}/{result['key_length']}

5. Ortak anahtar oluşturuldu
   └─ Anahtar uzunluğu: {result['shared_key_length']} bit

📊 SONUÇLAR:

  Gönderilen qubit:     {result['key_length']}
  Eşleşen basis:        {result['matching_bases']}
  Ortak anahtar:        {result['shared_key_length']} bit
  Hata oranı:           {result['error_rate']:.2%}
  
  Alice bitleri:  {' '.join(map(str, result['alice_bits'][:16]))}...
  Bob ölçümleri:  {' '.join(map(str, result['bob_measurements'][:16]))}...
  
  Final anahtar:  {' '.join(map(str, result['final_key']))}

🛡️ GÜVENLİK ANALİZİ:

  {'✅ GÜVENLI' if result['secure'] else '❌ DİNLENME TESPİT EDİLDİ'}
  
  Hata eşiği: %11 (teorik limit)
  Ölçülen hata: {result['error_rate']:.2%}

💡 KUANTUM ÖZELLİKLER:
  • Eve dinlerse qubit durumu bozulur
  • Hata oranı artar → tespit edilir
  • No-cloning teoremi sayesinde güvenli
"""
        
        self.quantum_results.insert(tk.END, output)
        self.log(f"🔐 BB84 simülasyonu tamamlandı - {'Güvenli' if result['secure'] else 'Dinleme var'}")
    
    def run_grover_test(self):
        """Grover algoritması güvenlik testi"""
        if self.encrypted_image is None:
            messagebox.showwarning("Uyarı", "Önce bir görüntü şifreleyin!")
            return
        
        self.quantum_results.delete('1.0', tk.END)
        self.quantum_results.insert('1.0', "🛡️ Grover güvenlik testi yapılıyor...\n\n")
        self.quantum_results.update()
        
        result = self.quantum_sim.grover_security_test(self.encrypted_image)
        
        output = f"""
╔══════════════════════════════════════════════════════════╗
║        🛡️ GROVER ALGORİTMASI GÜVENLİK TESTİ           ║
╚══════════════════════════════════════════════════════════╝

🔬 KUANTUM ARAMA ALGORİTMASI ANALİZİ

Grover algoritması, kuantum bilgisayarların yapılandırılmamış
aramada sağladığı hız avantajını ölçer.

📊 KARMAŞIKLIK ANALİZİ:

  Klasik arama:    O(N) = {result['classical_time']:,} işlem
  Grover arama:    O(√N) = {result['quantum_time']:,.0f} işlem
  Hız kazancı:     {result['grover_advantage']:.2f}x
  
  Görüntü boyutu:  {self.encrypted_image.shape[0]}×{self.encrypted_image.shape[1]}

🔐 GÜVENLİK METRİKLERİ:

  ┌─────────────────────────────────────────┐
  │  Entropi:        {result['entropy']:.4f} / 8.0000     │
  │  Tekrarsızlık:   {result['uniqueness']:.4f}           │
  │  Pattern direnç: {(result['score']/100)*30:.2f} / 30.0        │
  └─────────────────────────────────────────┘

🎯 GENEL GÜVENLİK SKORU:

  ███████████████████████████████████ {result['score']:.1f}/100
  
  {result['message']}

💡 DEĞERLENDİRME:

  • Entropi 7.99+ → Mükemmel rastgelelik
  • Tekrarsızlık 0.95+ → Pattern yok
  • Grover advantage yüksek → Kuantum'a dirençli

🔬 POST-QUANTUM HAZIRLIK:
  
  {'✅ Sistem kuantum bilgisayar saldırılarına hazır' if result['secure'] else '⚠️  Ek güvenlik önlemleri düşünülebilir'}
  
  Önerilen minimum skor: 85/100
  Mevcut skor: {result['score']:.1f}/100
"""
        
        self.quantum_results.insert(tk.END, output)
        self.log(f"🛡️ Grover testi: {result['score']:.1f}/100 - {result['message']}")
            
    def export_results(self):
        """Tüm sonuçları dışa aktar"""
        if self.encrypted_image is None:
            messagebox.showwarning("Uyarı", "Önce şifreleme yapın!")
            return
        
        folder = filedialog.askdirectory(title="Kayıt Klasörü Seç")
        
        if folder:
            try:
                cv2.imwrite(f"{folder}/encrypted.png", self.encrypted_image)
                if self.decrypted_image is not None:
                    cv2.imwrite(f"{folder}/decrypted.png", self.decrypted_image)
                
                # Metrikleri kaydet
                with open(f"{folder}/metrics.txt", 'w', encoding='utf-8') as f:
                    f.write(self.metrics_text.get(1.0, tk.END))
                
                self.log(f"📦 Tüm sonuçlar dışa aktarıldı: {folder}")
                messagebox.showinfo("Başarılı", "Dosyalar başarıyla kaydedildi!")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt hatası: {str(e)}")


def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    app = ChaosPolybiusGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
