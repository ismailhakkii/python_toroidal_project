"""
ChaosPolybius-2026 - Streamlit Web Arayuzu
Tkinter GUI'nin birebir web kopyasi
"""

import streamlit as st
import numpy as np
import cv2
import time
import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from encryption import encrypt_image_from_array, decrypt_image
from security_metrics import SecurityMetrics
from quantum_simulator import QuantumSimulator

# ===================================================================
#  SAYFA AYARLARI
# ===================================================================
st.set_page_config(
    page_title="ChaosPolybius-2026 - Kaotik Goruntu Sifreleme Sistemi",
    page_icon="\U0001f510",
    layout="wide",
)

# ===================================================================
#  CSS - Tkinter GUI renklerinin birebir karsiligi
# ===================================================================
st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; }
    .main-title {
        text-align: center; color: #7aa2f7;
        font-size: 28px; font-weight: bold;
        padding: 8px 0 0 0; margin: 0;
    }
    .main-subtitle {
        text-align: center; color: #ffffff;
        font-size: 14px; padding: 0 0 8px 0; margin: 0;
    }
    .panel-card {
        background-color: #2d2d44; border: 1px solid #3d3d5c;
        border-radius: 6px; padding: 12px; margin-bottom: 10px;
    }
    .panel-card h4 { color: #7aa2f7; margin: 0 0 8px 0; font-size: 14px; }
    .image-box {
        background-color: #2d2d44; border: 1px solid #3d3d5c;
        border-radius: 6px; padding: 30px 8px;
        text-align: center; color: #666; font-size: 13px;
    }
    .image-box-title {
        color: #cdd6f4; font-size: 13px;
        font-weight: bold; margin-bottom: 4px;
    }
    .log-box {
        background-color: #1e1e2e; border: 1px solid #3d3d5c;
        border-radius: 4px; padding: 10px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px; color: #9ece6a;
        max-height: 180px; overflow-y: auto; white-space: pre-wrap;
    }
    .log-title { color: #ffffff; font-weight: bold; font-size: 13px; }
    .metric-box {
        background-color: #1e1e2e; border: 1px solid #3d3d5c;
        border-radius: 4px; padding: 10px;
        font-family: 'Consolas', monospace;
        font-size: 11px; color: #ffffff;
        max-height: 280px; overflow-y: auto; white-space: pre-wrap;
    }
    .quantum-result-box {
        background-color: #1e1e2e; border: 1px solid #3d3d5c;
        border-radius: 4px; padding: 14px;
        font-family: 'Consolas', monospace;
        font-size: 12px; color: #cdd6f4;
        min-height: 400px; max-height: 600px;
        overflow-y: auto; white-space: pre-wrap;
    }
    .key-text-box {
        background-color: #1e1e2e; border: 1px solid #3d3d5c;
        border-radius: 4px; padding: 8px;
        font-family: 'Consolas', monospace;
        font-size: 11px; color: #cdd6f4; white-space: pre-wrap;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #2d2d44; border-radius: 6px; padding: 4px;
    }
    .stTabs [data-baseweb="tab"] { color: #cdd6f4; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #7aa2f7 !important; }
    .stButton > button {
        background-color: #7aa2f7; color: #ffffff;
        font-weight: bold; border: none; border-radius: 4px;
    }
    .stButton > button:hover { background-color: #89b4fa; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #2d2d44; }
    .stNumberInput label { color: #cdd6f4 !important; }
    header[data-testid="stHeader"] { background-color: #1e1e2e; }
</style>
""", unsafe_allow_html=True)


# ===================================================================
#  SESSION STATE
# ===================================================================
_defaults = {
    "original": None, "encrypted": None, "decrypted": None,
    "log_lines": ["Sistem hazir. Goruntu yukleyin veya parametreleri ayarlayin."],
    "metrics_text": "", "quantum_result_text": "", "quantum_key": "",
    "random_key": None,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def add_log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state["log_lines"].append("[" + ts + "] " + msg)
    st.session_state["log_lines"] = st.session_state["log_lines"][-50:]


def get_log_text():
    return "\n".join(st.session_state["log_lines"])


def to_png(arr):
    _, buf = cv2.imencode(".png", arr)
    return buf.tobytes()


# ===================================================================
#  BASLIK
# ===================================================================
st.markdown('<p class="main-title">\U0001f510 ChaosPolybius-2026</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Geri Beslemeli Pertürbasyon ve Toroidal Graf ile Görüntü Şifreleme</p>', unsafe_allow_html=True)


# ===================================================================
#  TABLAR
# ===================================================================
tab_encrypt, tab_quantum = st.tabs(["\U0001f512 Şifreleme", "\U0001f52c Kuantum Simülasyonu"])


# -------------------------------------------------------------------
#  TAB 1 - SIFRELEME
# -------------------------------------------------------------------
with tab_encrypt:

    col_left, col_right = st.columns([1, 2.6], gap="medium")

    # ========== SOL PANEL ==========
    with col_left:

        # Dosya islemleri
        st.markdown('<div class="panel-card"><h4>\U0001f4c1 Dosya İşlemleri</h4></div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Goruntu Yukle", type=["png","jpg","jpeg","bmp"],
                                    label_visibility="collapsed")
        if uploaded is not None:
            fbytes = np.frombuffer(uploaded.read(), np.uint8)
            img = cv2.imdecode(fbytes, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                st.session_state["original"] = img
                st.session_state["encrypted"] = None
                st.session_state["decrypted"] = None
                add_log("Goruntu yuklendi: " + uploaded.name)
                add_log("   Boyut: " + str(img.shape))

        dl1, dl2 = st.columns(2)
        with dl1:
            if st.session_state["encrypted"] is not None:
                st.download_button("Sifreli Goruntu Kaydet",
                                   to_png(st.session_state["encrypted"]),
                                   "encrypted.png", "image/png",
                                   use_container_width=True)
        with dl2:
            if st.session_state["decrypted"] is not None:
                st.download_button("Sonuclari Disa Aktar",
                                   to_png(st.session_state["decrypted"]),
                                   "decrypted.png", "image/png",
                                   use_container_width=True)

        # Anahtar parametreleri
        st.markdown('<div class="panel-card"><h4>\U0001f511 Anahtar Parametreleri</h4></div>', unsafe_allow_html=True)

        key_labels = ["x0", "u0", "r", "a", "b", "c", "delta"]
        key_defaults = [0.5, 0.3, 3.99, 0.2, 0.3, 0.4, 0.1]
        if st.session_state["random_key"] is not None:
            key_defaults = st.session_state["random_key"]

        key_vals = []
        kc1, kc2 = st.columns(2)
        for i, (lbl, dflt) in enumerate(zip(key_labels, key_defaults)):
            with kc1 if i % 2 == 0 else kc2:
                mn, mx = (3.57, 4.0) if lbl == "r" else (0.0, 1.0)
                v = st.number_input(lbl, mn, mx, float(dflt), 0.0001,
                                    format="%.4f", key="k_" + lbl)
                key_vals.append(v)
        base_key = key_vals

        bk1, bk2 = st.columns(2)
        with bk1:
            if st.button("Anahtari Guncelle", use_container_width=True):
                add_log("Anahtar parametreleri guncellendi")
                add_log("   Yeni anahtar: " + str([round(v, 4) for v in base_key]))
        with bk2:
            if st.button("Rastgele Anahtar", use_container_width=True):
                import random
                rk = [
                    random.uniform(0.1, 0.9), random.uniform(0.1, 0.9),
                    random.uniform(3.7, 4.0), random.uniform(0.1, 0.5),
                    random.uniform(0.1, 0.5), random.uniform(0.1, 0.5),
                    random.uniform(0.05, 0.2),
                ]
                st.session_state["random_key"] = rk
                add_log("Rastgele anahtar olusturuldu")
                st.rerun()

        # Sifreleme
        st.markdown('<div class="panel-card"><h4>\u2699\ufe0f Şifreleme</h4></div>', unsafe_allow_html=True)

        bc1, bc2 = st.columns(2)
        with bc1:
            encrypt_btn = st.button("\U0001f512 SIFRELE", use_container_width=True, type="primary")
        with bc2:
            decrypt_btn = st.button("\U0001f513 DESIFRELE", use_container_width=True)

        if encrypt_btn:
            if st.session_state["original"] is None:
                st.warning("Once bir goruntu yukleyin!")
            else:
                add_log("Sifreleme basliyor...")
                t0 = time.time()
                enc = encrypt_image_from_array(st.session_state["original"], base_key)
                elapsed = (time.time() - t0) * 1000
                st.session_state["encrypted"] = enc
                st.session_state["decrypted"] = None
                add_log("Sifreleme tamamlandi (" + str(round(elapsed, 1)) + " ms)")
                st.rerun()

        if decrypt_btn:
            if st.session_state["encrypted"] is None:
                st.warning("Once sifreleme yapin!")
            elif st.session_state["original"] is None:
                st.warning("Orijinal goruntu gerekli!")
            else:
                add_log("Desifreleme basliyor...")
                t0 = time.time()
                dec = decrypt_image(
                    st.session_state["encrypted"], base_key,
                    st.session_state["original"]
                )
                elapsed = (time.time() - t0) * 1000
                st.session_state["decrypted"] = dec
                mse = float(np.mean(
                    (st.session_state["original"].astype(float) - dec.astype(float)) ** 2
                ))
                add_log("Desifreleme tamamlandi (" + str(round(elapsed, 1)) + " ms)")
                if mse == 0:
                    add_log("   MSE: 0.000000 BASARILI")
                else:
                    add_log("   MSE: " + str(round(mse, 6)) + " HATA")
                st.rerun()

        # Guvenlik metrikleri
        st.markdown('<div class="panel-card"><h4>\U0001f4ca Güvenlik Metrikleri</h4></div>', unsafe_allow_html=True)

        if st.button("Metrikleri Hesapla", use_container_width=True):
            orig = st.session_state["original"]
            enc = st.session_state["encrypted"]
            if orig is None or enc is None:
                st.warning("Once sifreleme yapin!")
            else:
                add_log("Metrikler hesaplaniyor...")
                entropy_orig = SecurityMetrics.entropy(orig)
                entropy_enc = SecurityMetrics.entropy(enc)
                corr_h = SecurityMetrics.correlation(enc, "horizontal")
                corr_v = SecurityMetrics.correlation(enc, "vertical")

                mod = orig.copy()
                mod[0, 0] = np.uint8((int(mod[0, 0]) + 1) % 256)
                e1 = encrypt_image_from_array(orig, base_key)
                e2 = encrypt_image_from_array(mod, base_key)
                npcr = SecurityMetrics.npcr(e1, e2)
                uaci = SecurityMetrics.uaci(e1, e2)

                ent_ok = "GECTI" if entropy_enc > 7.99 else "BASARISIZ"
                cor_ok = "GECTI" if abs(corr_h) < 0.01 else "YUKSEK"
                npcr_ok = "GECTI" if npcr > 99.60 else "DUSUK"
                uaci_ok = "GECTI" if 33.28 < uaci < 33.64 else "SINIR DISI"

                txt = (
                    "==============================\n"
                    "   GUVENLIK METRIKLERI\n"
                    "==============================\n\n"
                    "ENTROPI\n"
                    "  Orijinal:  " + str(round(entropy_orig, 4)) + " bit\n"
                    "  Sifreli:   " + str(round(entropy_enc, 4)) + " bit\n"
                    "  Hedef:     8.0000 bit\n"
                    "  Durum:     " + ent_ok + "\n\n"
                    "KORELASYON\n"
                    "  Yatay:     " + str(round(corr_h, 6)) + "\n"
                    "  Dikey:     " + str(round(corr_v, 6)) + "\n"
                    "  Hedef:     0.0000\n"
                    "  Durum:     " + cor_ok + "\n\n"
                    "DIFERANSIYEL ANALIZ\n"
                    "  NPCR:      " + str(round(npcr, 4)) + "%\n"
                    "  Hedef:     >99.60%\n"
                    "  Durum:     " + npcr_ok + "\n\n"
                    "  UACI:      " + str(round(uaci, 4)) + "%\n"
                    "  Hedef:     33.28-33.64%\n"
                    "  Durum:     " + uaci_ok + "\n\n"
                    "==============================\n"
                    "GENEL SONUC: " + ("BASARILI" if (entropy_enc > 7.99 and abs(corr_h) < 0.01) else "INCELE") + "\n"
                )
                st.session_state["metrics_text"] = txt
                add_log("Metrikler hesaplandi")
                st.rerun()

        if st.session_state["metrics_text"]:
            st.markdown(
                '<div class="metric-box">' + st.session_state["metrics_text"] + '</div>',
                unsafe_allow_html=True,
            )

    # ========== SAG PANEL - 2x2 Goruntu Grid ==========
    with col_right:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.markdown('<p class="image-box-title">\U0001f4f7 Orijinal Görüntü</p>', unsafe_allow_html=True)
            if st.session_state["original"] is not None:
                st.image(st.session_state["original"], clamp=True, use_container_width=True)
            else:
                st.markdown('<div class="image-box">Goruntu yok</div>', unsafe_allow_html=True)

        with r1c2:
            st.markdown('<p class="image-box-title">\U0001f512 Şifreli Görüntü</p>', unsafe_allow_html=True)
            if st.session_state["encrypted"] is not None:
                st.image(st.session_state["encrypted"], clamp=True, use_container_width=True)
            else:
                st.markdown('<div class="image-box">Sifreleme yapilmadi</div>', unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.markdown('<p class="image-box-title">\U0001f513 Deşifreli Görüntü</p>', unsafe_allow_html=True)
            if st.session_state["decrypted"] is not None:
                st.image(st.session_state["decrypted"], clamp=True, use_container_width=True)
            else:
                st.markdown('<div class="image-box">Desifreleme yapilmadi</div>', unsafe_allow_html=True)

        with r2c2:
            st.markdown('<p class="image-box-title">\U0001f4c8 Histogram</p>', unsafe_allow_html=True)
            if st.session_state["encrypted"] is not None:
                enc_img = st.session_state["encrypted"]
                fig, ax = plt.subplots(figsize=(4, 3))
                fig.patch.set_facecolor("#2d2d44")
                ax.set_facecolor("#2d2d44")
                hist_v = cv2.calcHist([enc_img], [0], None, [256], [0, 256]).ravel()
                ax.bar(range(256), hist_v, width=1.0, color="#7aa2f7", edgecolor="none")
                ax.tick_params(colors="#cdd6f4", labelsize=7)
                for sp in ["top", "right"]:
                    ax.spines[sp].set_visible(False)
                for sp in ["bottom", "left"]:
                    ax.spines[sp].set_color("#3d3d5c")
                fig.tight_layout(pad=1)
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.markdown('<div class="image-box">Histogram yok</div>', unsafe_allow_html=True)


# -------------------------------------------------------------------
#  TAB 2 - KUANTUM SIMULASYONU
# -------------------------------------------------------------------
with tab_quantum:

    qsim = QuantumSimulator()
    qcol_left, qcol_right = st.columns([1, 2.2], gap="medium")

    with qcol_left:
        st.markdown(
            '<div class="panel-card" style="text-align:center;">'
            '<h4>\U0001f52c Kuantum Kriptografi</h4></div>',
            unsafe_allow_html=True,
        )

        # QRNG
        st.markdown(
            '<div class="panel-card"><h4>Kuantum Rastgele Anahtar Ureteci</h4>'
            '<p style="color:#cdd6f4;font-size:12px;">'
            'Superpozisyon ve olcum belirsizligi<br>'
            'ile gercek rastgele anahtar uretir.</p></div>',
            unsafe_allow_html=True,
        )

        if st.button("Kuantum Anahtar Uret", use_container_width=True, key="q_qrng"):
            qkey = qsim.generate_quantum_random_key(7)
            txt = (
                "========================================================\n"
                "         KUANTUM RASTGELE ANAHTAR URETICI\n"
                "========================================================\n\n"
                "Metod: Superpozisyon + Kuantum Olcumu\n"
                "Qubit Sayisi: 8 qubit per parametre\n"
                "Belirsizlik: Heisenberg Ilkesi\n\n"
                "URETILEN ANAHTAR:\n\n"
                "  x0    = " + str(round(qkey[0], 6)) + "  (Ilk durum - FPLM)\n"
                "  u0    = " + str(round(qkey[1], 6)) + "  (Ikinci durum - FPLM)\n"
                "  r     = " + str(round(qkey[2], 6)) + "  (Kaos parametresi)\n"
                "  a     = " + str(round(qkey[3], 6)) + "  (Perturbasyon 1)\n"
                "  b     = " + str(round(qkey[4], 6)) + "  (Perturbasyon 2)\n"
                "  c     = " + str(round(qkey[5], 6)) + "  (Perturbasyon 3)\n"
                "  delta = " + str(round(qkey[6], 6)) + "  (Geri besleme orani)\n\n"
                "Kuantum Ozellikler:\n"
                "  - Her olcum tamamen farklidir (belirsizlik)\n"
                "  - Klasik RNG'den daha rastgele\n"
                "  - Tahmin edilemez (no-cloning teoremi)\n\n"
                "Bu anahtari sifreleme icin kullanabilirsiniz!\n"
                "\"Anahtari Kullan\" butonuna basin.\n"
            )
            st.session_state["quantum_result_text"] = txt
            st.session_state["quantum_key"] = str([round(x, 6) for x in qkey])
            add_log("Kuantum anahtar uretildi")
            st.rerun()

        if st.session_state["quantum_key"]:
            st.markdown(
                '<div class="key-text-box">' + st.session_state["quantum_key"] + '</div>',
                unsafe_allow_html=True,
            )

        if st.button("Anahtari Kullan", use_container_width=True, key="q_use"):
            if st.session_state["quantum_key"]:
                import ast
                try:
                    rk = ast.literal_eval(st.session_state["quantum_key"])
                    st.session_state["random_key"] = rk
                    add_log("Kuantum anahtar aktif edildi")
                    st.success("Kuantum anahtar sifreleme icin hazir!")
                except Exception:
                    st.warning("Once bir kuantum anahtar uretin!")
            else:
                st.warning("Once bir kuantum anahtar uretin!")

        # BB84
        st.markdown(
            '<div class="panel-card"><h4>BB84 Kuantum Anahtar Dagitimi</h4>'
            '<p style="color:#cdd6f4;font-size:12px;">'
            'Alice ve Bob guvenli anahtar paylasir.<br>'
            'Dinleme (Eve) tespit edilir.</p></div>',
            unsafe_allow_html=True,
        )

        if st.button("BB84 Simulasyonu Calistir", use_container_width=True, key="q_bb84"):
            r = qsim.bb84_simulation(32)
            sec_txt = "GUVENLI" if r["secure"] else "DINLENME TESPIT EDILDI"
            txt = (
                "========================================================\n"
                "       BB84 KUANTUM ANAHTAR DAGITIMI\n"
                "========================================================\n\n"
                "PROTOKOL ADIMLARI:\n\n"
                "1. Alice " + str(r["key_length"]) + " qubit hazirlar\n"
                "   - Rastgele bit + rastgele basis secimi\n\n"
                "2. Alice -> Bob (kuantum kanal)\n"
                "   - Qubitler gonderilir\n\n"
                "3. Bob olcum yapar\n"
                "   - Rastgele basis secimi\n\n"
                "4. Alice <-> Bob basis karsilastirmasi (klasik kanal)\n"
                "   - Eslesen bazlar: " + str(r["matching_bases"]) + "/" + str(r["key_length"]) + "\n\n"
                "5. Ortak anahtar olusturuldu\n"
                "   - Anahtar uzunlugu: " + str(r["shared_key_length"]) + " bit\n\n"
                "SONUCLAR:\n\n"
                "  Gonderilen qubit:     " + str(r["key_length"]) + "\n"
                "  Eslesen basis:        " + str(r["matching_bases"]) + "\n"
                "  Ortak anahtar:        " + str(r["shared_key_length"]) + " bit\n"
                "  Hata orani:           " + str(round(r["error_rate"] * 100, 2)) + "%\n\n"
                "  Alice bitleri:  " + " ".join(map(str, r["alice_bits"][:16])) + "...\n"
                "  Bob olcumleri:  " + " ".join(map(str, r["bob_measurements"][:16])) + "...\n\n"
                "  Final anahtar:  " + " ".join(map(str, r["final_key"])) + "\n\n"
                "GUVENLIK ANALIZI:\n\n"
                "  " + sec_txt + "\n\n"
                "  Hata esigi: %11 (teorik limit)\n"
                "  Olculen hata: " + str(round(r["error_rate"] * 100, 2)) + "%\n\n"
                "KUANTUM OZELLIKLER:\n"
                "  - Eve dinlerse qubit durumu bozulur\n"
                "  - Hata orani artar -> tespit edilir\n"
                "  - No-cloning teoremi sayesinde guvenli\n"
            )
            st.session_state["quantum_result_text"] = txt
            add_log("BB84 simulasyonu tamamlandi - " + ("Guvenli" if r["secure"] else "Dinleme var"))
            st.rerun()

        # Grover
        st.markdown(
            '<div class="panel-card"><h4>Grover Guvenlik Testi</h4>'
            '<p style="color:#cdd6f4;font-size:12px;">'
            'Kuantum bilgisayar saldirilarina<br>'
            'karsi guvenlik analizi.</p></div>',
            unsafe_allow_html=True,
        )

        if st.button("Guvenlik Testi Yap", use_container_width=True, key="q_grover"):
            if st.session_state["encrypted"] is None:
                st.warning("Once bir goruntu sifreleyin!")
            else:
                r = qsim.grover_security_test(st.session_state["encrypted"])
                sh = st.session_state["encrypted"].shape
                pq_txt = "Sistem kuantum bilgisayar saldirilarina hazir" if r["secure"] else "Ek guvenlik onlemleri dusunulebilir"
                txt = (
                    "========================================================\n"
                    "      GROVER ALGORITMASI GUVENLIK TESTI\n"
                    "========================================================\n\n"
                    "KUANTUM ARAMA ALGORITMASI ANALIZI\n\n"
                    "Grover algoritmasi, kuantum bilgisayarlarin yapilandirilmamis\n"
                    "aramada sagladigi hiz avantajini olcer.\n\n"
                    "KARMASIKLIK ANALIZI:\n\n"
                    "  Klasik arama:    O(N) = " + str(r["classical_time"]) + " islem\n"
                    "  Grover arama:    O(vN) = " + str(round(r["quantum_time"])) + " islem\n"
                    "  Hiz kazanci:     " + str(round(r["grover_advantage"], 2)) + "x\n\n"
                    "  Goruntu boyutu:  " + str(sh[0]) + "x" + str(sh[1]) + "\n\n"
                    "GUVENLIK METRIKLERI:\n\n"
                    "  Entropi:        " + str(round(r["entropy"], 4)) + " / 8.0000\n"
                    "  Tekrarsizlik:   " + str(round(r["uniqueness"], 4)) + "\n"
                    "  Pattern direnc: " + str(round((r["score"]/100)*30, 2)) + " / 30.0\n\n"
                    "GENEL GUVENLIK SKORU:\n\n"
                    "  " + str(round(r["score"], 1)) + "/100\n\n"
                    "  " + r["message"] + "\n\n"
                    "DEGERLENDIRME:\n\n"
                    "  - Entropi 7.99+ -> Mukemmel rastgelelik\n"
                    "  - Tekrarsizlik 0.95+ -> Pattern yok\n"
                    "  - Grover advantage yuksek -> Kuantum'a direncli\n\n"
                    "POST-QUANTUM HAZIRLIK:\n\n"
                    "  " + pq_txt + "\n\n"
                    "  Onerilen minimum skor: 85/100\n"
                    "  Mevcut skor: " + str(round(r["score"], 1)) + "/100\n"
                )
                st.session_state["quantum_result_text"] = txt
                add_log("Grover testi: " + str(round(r["score"], 1)) + "/100 - " + r["message"])
                st.rerun()

    # Sag panel - Sonuclar
    with qcol_right:
        st.markdown(
            '<div class="panel-card" style="text-align:center;">'
            '<h4>Kuantum Simulasyon Sonuclari</h4></div>',
            unsafe_allow_html=True,
        )

        qtxt = st.session_state["quantum_result_text"]
        if not qtxt:
            qtxt = (
                "========================================================\n"
                "        KUANTUM KRIPTOGRAFI SIMULATORU\n"
                "========================================================\n\n"
                "Bu modul, kuantum bilgisayar ve kuantum kriptografi\n"
                "konseptlerini simule eder.\n\n"
                "OZELLIKLER:\n\n"
                "1. Kuantum Rastgele Sayi Ureteci (QRNG)\n"
                "   - Superpozisyon prensibini kullanir\n"
                "   - Gercek rastgele anahtar uretir\n"
                "   - Klasik RNG'den daha guvenli\n\n"
                "2. BB84 Protokolu\n"
                "   - Kuantum anahtar dagitim simulasyonu\n"
                "   - Alice <-> Bob guvenli iletisim\n"
                "   - Dinleme tespit mekanizmasi\n\n"
                "3. Grover Algoritmasi Guvenlik Testi\n"
                "   - Kuantum arama algoritmasi simulasyonu\n"
                "   - Sifreli goruntu guvenlik analizi\n"
                "   - Post-quantum crypto degerlendirmesi\n\n"
                "NOT: Bu simulasyonlar egitici amaclidir.\n"
                "   Gercek kuantum bilgisayar gerektirmez.\n\n"
                "Baslamak icin sol panelden bir islem secin!\n"
            )

        st.markdown(
            '<div class="quantum-result-box">' + qtxt + '</div>',
            unsafe_allow_html=True,
        )


# ===================================================================
#  ALT PANEL - ISLEM GUNLUGU
# ===================================================================
st.markdown("---")
st.markdown('<p class="log-title">Islem Gunlugu</p>', unsafe_allow_html=True)
st.markdown('<div class="log-box">' + get_log_text() + '</div>', unsafe_allow_html=True)
