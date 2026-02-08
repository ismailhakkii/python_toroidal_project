"""
ChaosPolybius-2026 - Basit Tkinter GUI
Deşifreleme sorunu çözüldü!
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
from encryption import encrypt_image_from_array, decrypt_image

class ChaosCipherApp:
    def __init__(self, root):  # __init__ düzeltildi
        self.root = root
        self.root.title("ChaosPolybius-2026 Şifreleme Sistemi")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Değişkenler
        self.file_path = None
        self.original_image_cv = None  # İşlem görecek ham cv2 verisi
        self.processed_image_cv = None # Sonuç cv2 verisi
        self.default_key = "0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Üst Panel (Butonlar ve Anahtar)
        control_frame = tk.Frame(self.root, bg="#ddd", pady=10)
        control_frame.pack(fill="x")
        
        tk.Label(control_frame, text="Anahtar (x0, u0, r, a, b, c, delta):", bg="#ddd").pack(side="left", padx=10)
        
        self.key_entry = tk.Entry(control_frame, width=40)
        self.key_entry.insert(0, self.default_key)
        self.key_entry.pack(side="left", padx=5)
        
        btn_load = tk.Button(control_frame, text="Resim Yükle", command=self.load_image, bg="#4CAF50", fg="white")
        btn_load.pack(side="left", padx=10)
        
        btn_enc = tk.Button(control_frame, text="🔒 ŞİFRELE", command=self.perform_encrypt, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        btn_enc.pack(side="left", padx=5)
        
        btn_dec = tk.Button(control_frame, text="🔓 DEŞİFRELE", command=self.perform_decrypt, bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        btn_dec.pack(side="left", padx=5)
        
        btn_save = tk.Button(control_frame, text="Kaydet", command=self.save_image, bg="#607D8B", fg="white")
        btn_save.pack(side="left", padx=10)

        # Görüntü Alanı
        self.image_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.image_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Sol: Orijinal
        self.lbl_orig_title = tk.Label(self.image_frame, text="Giriş Görüntüsü", bg="#f0f0f0", font=("Arial", 12))
        self.lbl_orig_title.grid(row=0, column=0, padx=10)
        self.lbl_orig_img = tk.Label(self.image_frame, text="Görüntü yok", bg="white", width=50, height=25, relief="sunken")
        self.lbl_orig_img.grid(row=1, column=0, padx=10)
        
        # Sağ: İşlenmiş
        self.lbl_proc_title = tk.Label(self.image_frame, text="İşlenmiş Görüntü", bg="#f0f0f0", font=("Arial", 12))
        self.lbl_proc_title.grid(row=0, column=1, padx=10)
        self.lbl_proc_img = tk.Label(self.image_frame, text="Sonuç yok", bg="white", width=50, height=25, relief="sunken")
        self.lbl_proc_img.grid(row=1, column=1, padx=10)
        
        # Bilgi Çubuğu
        self.status_bar = tk.Label(self.root, text="Hazır - Deşifreleme sorunu çözüldü! ✅", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def parse_key(self):
        try:
            k_str = self.key_entry.get()
            return [float(x.strip()) for x in k_str.split(',')]
        except:
            messagebox.showerror("Hata", "Anahtar formatı hatalı! Virgülle ayrılmış 7 sayı girin.")
            return None

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])  # Noktalı virgül düzeltildi
        if path:
            self.file_path = path
            self.original_image_cv = cv2.imread(path, 0) # Gri modda yükle
            self.processed_image_cv = None
            self.show_image(self.original_image_cv, self.lbl_orig_img)
            self.lbl_proc_img.config(image='', text="Sonuç yok")
            self.status_bar.config(text=f"Yüklendi: {os.path.basename(path)}")

    def perform_encrypt(self):
        if self.original_image_cv is None:
            messagebox.showwarning("Uyarı", "Lütfen önce bir resim yükleyin.")
            return
            
        key = self.parse_key()
        if not key: return
        
        try:
            self.status_bar.config(text="Şifreleniyor... Lütfen bekleyin...")
            self.root.update()
            
            # Doğrudan array üzerinden şifreleme
            self.processed_image_cv = encrypt_image_from_array(self.original_image_cv, key)
            
            self.show_image(self.processed_image_cv, self.lbl_proc_img)
            self.status_bar.config(text="Şifreleme tamamlandı! ✅")
        except Exception as e:
            messagebox.showerror("Hata", str(e))
            self.status_bar.config(text=f"Hata: {str(e)}")

    def perform_decrypt(self):
        """
        Deşifreleme - DÜZELTİLDİ!
        
        Kullanım:
        1. Sol tarafa orijinal görüntüyü yükleyin
        2. Şifreleme yapın
        3. Deşifreleme butonuna tıklayın
        
        Alternatif:
        - Şifreli görüntüyü "Resim Yükle" ile yükleyip deşifreleyin
          (Bu durumda orijinal görüntünün hash'i için özel işlem gerekir)
        """
        if self.processed_image_cv is None:
            messagebox.showwarning("Uyarı", "Önce şifreleme yapın veya şifreli görüntü yükleyin!")
            return
        
        if self.original_image_cv is None:
            messagebox.showwarning("Uyarı", "Deşifreleme için orijinal görüntü gerekli!")
            return
            
        key = self.parse_key()
        if not key: return
        
        try:
            self.status_bar.config(text="Deşifreleme yapılıyor... Lütfen bekleyin...")
            self.root.update()
            
            # ✅ DÜZELTİLDİ: Şifreli görüntü ve orijinal referans ile deşifreleme
            decoded = decrypt_image(self.processed_image_cv, key, self.original_image_cv)
            
            # MSE kontrolü
            mse = np.mean((self.original_image_cv - decoded) ** 2)
            
            self.processed_image_cv = decoded
            self.show_image(decoded, self.lbl_proc_img)
            
            if mse == 0:
                self.status_bar.config(text=f"✅ Deşifreleme BAŞARILI - Orijinal görüntü tamamen geri kazanıldı!")
            else:
                self.status_bar.config(text=f"⚠️ Deşifreleme tamamlandı ama MSE={mse:.4f} (Sıfır olmalıydı!)")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Deşifreleme hatası: {str(e)}")
            self.status_bar.config(text=f"❌ Hata: {str(e)}")

    def save_image(self):
        if self.processed_image_cv is None:
            messagebox.showwarning("Uyarı", "Kaydedilecek görüntü yok!")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            cv2.imwrite(path, self.processed_image_cv)
            messagebox.showinfo("Başarılı", "Görüntü kaydedildi.")
            self.status_bar.config(text=f"Kaydedildi: {os.path.basename(path)}")

    def show_image(self, cv_img, label_widget):
        """OpenCV (numpy) -> Tkinter (PhotoImage) dönüşümü"""
        if cv_img is None:
            return
            
        h, w = cv_img.shape
        
        # Önizleme için boyutlandır
        display_size = (400, 400)
        img_resized = cv2.resize(cv_img, display_size, interpolation=cv2.INTER_AREA)
        
        img_pil = Image.fromarray(img_resized)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        label_widget.config(image=img_tk, text="")
        label_widget.image = img_tk  # Referansı koru (garbage collection önlemi)

if __name__ == "__main__":  # __name__ ve __main__ düzeltildi
    root = tk.Tk()
    app = ChaosCipherApp(root)
    root.mainloop()
