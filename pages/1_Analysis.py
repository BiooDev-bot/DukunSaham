import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import io
from model import analisis
import yfinance as yf
# cek state dari app.py
required_keys = ["headline", "ticker", "price", "tanggal"]
missing = [k for k in required_keys if k not in st.session_state]
if missing:
    st.error("❌ Input belum lengkap. Silakan kembali ke halaman utama dan lakukan prediksi terlebih dahulu.")
    st.stop()

headline = st.session_state["headline"]
ticker = st.session_state["ticker"]
price_before = st.session_state["price"]
start_date = st.session_state["tanggal"]
end_date = start_date + timedelta(days=7)  # contoh: 7 hari setelah berita

# load model & scaler dari modul analisis
scaler, xgb_model, emb_model = analisis.load_all_models()
lime_explainer, predict_texts = analisis.build_lime_explainer(
    emb_model, xgb_model, analisis.num_feat_dim
)

pred = analisis.predict_headline_with_ticker(
    headline=headline,
    ticker=ticker,
    start_date=start_date,
    end_date=end_date,
    price_before=price_before,
    model=xgb_model,
    scaler=scaler,
    sent_model=emb_model,
    lime_explainer=lime_explainer,
    predict_texts=predict_texts,
    explain=True
)

st.session_state["pred"] = pred
# ----------------------------
# Konfigurasi halaman
# ----------------------------
st.set_page_config(page_title="Analisis Saham ANTM", page_icon="💹", layout="centered")

# Tema warna
BG_DARK = "#0E1117"
TEXT_GRAY = "#BBBBBB"
TEXT_LIGHT = "#FFFFFF"

# ----------------------------
# Judul
# ----------------------------
st.markdown(
    f"""
    <h2 style='text-align:center; color:{TEXT_LIGHT}; margin-bottom:0;'>📊 Hasil Prediksi Perubahan Harga Saham</h2>
    <p style='text-align:center; color:{TEXT_GRAY}; font-size:14px; margin-top:2px;'>
        Indikator arah pergerakan harga berdasarkan analisis model
    </p>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Input nilai prediksi
# ----------------------------
prediksi_persen = (st.session_state["pred"])*100

# Warna angka dinamis
if prediksi_persen < -1:
    warna_teks = "#FF4B4B"   # Merah (Sell)
elif prediksi_persen < 1:
    warna_teks = "#FFB300"   # Kuning/Oranye (Netral)
else:
    warna_teks = "#00C853"   # Hijau (Buy)

# ----------------------------
# Angka besar di tengah
# ----------------------------
st.markdown(
    f"""
    <h1 style='text-align:center; color:{warna_teks}; font-size:70px; margin-top:20px; margin-bottom:10px; transition: color 0.5s ease;'>
        {prediksi_persen}%
    </h1>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Gradasi bar (Sell → Buy)
# ----------------------------
fig, ax = plt.subplots(figsize=(10, 1.0))
gradient = np.linspace(0, 1, 512).reshape(1, -1)
ax.imshow(gradient, aspect='auto', cmap='RdYlGn', extent=[-100, 100, 0, 1])

ax.axvline(prediksi_persen, color='white', linewidth=3)
ax.set_xticks([-100, 0, 100])
ax.set_xticklabels(['Sell', 'Netral', 'Buy'], color='white', fontsize=12)
ax.set_yticks([])

for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='x', pad=10)

fig.patch.set_facecolor(BG_DARK)
ax.set_facecolor(BG_DARK)

buf = io.BytesIO()
plt.savefig(buf, format="png", bbox_inches="tight", facecolor=BG_DARK)
st.image(buf)

# ----------------------------
# Keterangan bawah
# ----------------------------
st.markdown(
    f"""
    <p style='text-align:center; color:{TEXT_GRAY}; font-size:13px; margin-top:5px;'>
        Semakin hijau berarti potensi harga <b>naik (Buy)</b>, semakin merah berarti potensi <b>turun (Sell)</b>.
    </p>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 🔽 TAMBAHAN: Grafik Tren Harga Terbaru
# =========================================================
st.markdown("<hr style='border: 0.5px solid #333;'>", unsafe_allow_html=True)

st.markdown(
    f"""
    <h4 style='text-align:center; color:{TEXT_LIGHT}; margin-bottom:5px;'>📈 Tren Harga 7 Hari Terakhir</h4>
    <p style='text-align:center; color:{TEXT_GRAY}; font-size:13px; margin-top:0px;'>
        Grafik berikut menampilkan pergerakan harga harian untuk memberikan konteks tambahan terhadap hasil prediksi.
    </p>
    """,
    unsafe_allow_html=True
)

# Data dummy tren harga
history = yf.download(
    f"{ticker}.JK",
    start=(start_date - pd.Timedelta(days=14)).strftime("%Y-%m-%d"),
    end=start_date.strftime("%Y-%m-%d"),
    progress=False
)

if history.empty:
    df = pd.DataFrame(columns=["Tanggal", "Harga"])
else:
    history = history.tail(7).copy()

    # reset index supaya Tanggal jadi kolom biasa
    history = history.reset_index()   # sekarang ada kolom 'Date'

    df = history[["Date", "Close"]].rename(
        columns={"Date": "Tanggal", "Close": "Harga"}
    )

# Plot
fig2, ax2 = plt.subplots(figsize=(10, 3))
ax2.plot(df["Tanggal"], df["Harga"], color=warna_teks, linewidth=3, marker='o')
ax2.set_facecolor(BG_DARK)
fig2.patch.set_facecolor(BG_DARK)
ax2.tick_params(colors=TEXT_GRAY, labelsize=10)
ax2.spines['bottom'].set_color(TEXT_GRAY)
ax2.spines['left'].set_color(TEXT_GRAY)
ax2.set_xlabel("Tanggal", color=TEXT_GRAY, fontsize=10)
ax2.set_ylabel("Harga (IDR)", color=TEXT_GRAY, fontsize=10)
ax2.grid(alpha=0.3, color="#444")

st.pyplot(fig2)

# =========================================================
# 📊 TAMBAHAN: Tingkat Volatilitas Pasar
# =========================================================
st.markdown("<hr style='border: 0.5px solid #333;'>", unsafe_allow_html=True)

st.markdown(
    f"""
    <h4 style='text-align:center; color:{TEXT_LIGHT}; margin-bottom:5px;'>🌪 Tingkat Volatilitas Pasar</h4>
    <p style='text-align:center; color:{TEXT_GRAY}; font-size:13px; margin-top:0px;'>
        Volatilitas menggambarkan seberapa besar fluktuasi harga dalam jangka pendek.
    </p>
    """,
    unsafe_allow_html=True
)

# Simulasi volatilitas (random antara 0 dan 100)
volatilitas = analisis.vol(ticker,start_date,end_date)
volatilitas = round(volatilitas * 100, 3)
# Tentukan warna dan deskripsi volatilitas
if volatilitas < 30:
    vol_color = "#00C853"
    vol_text = "Rendah — pasar relatif stabil."
elif volatilitas < 70:
    vol_color = "#FFB300"
    vol_text = "Sedang — fluktuasi harga mulai meningkat."
else:
    vol_color = "#FF4B4B"
    vol_text = "Tinggi — risiko pergerakan harga besar."

# Tampilan angka volatilitas besar
st.markdown(
    f"""
    <h1 style='text-align:center; color:{vol_color}; font-size:60px; margin-top:10px;'>{volatilitas}%</h1>
    <p style='text-align:center; color:{vol_color}; font-size:16px; margin-top:-10px;'><b>{vol_text}</b></p>
    """,
    unsafe_allow_html=True
)

# Progress bar indikator volatilitas
progress_html = f"""
<div style='background-color:#222; border-radius:10px; height:20px; width:80%; margin:auto;'>
  <div style='height:100%; width:{volatilitas}%; background-color:{vol_color}; border-radius:10px;'></div>
</div>
"""
st.markdown(progress_html, unsafe_allow_html=True)

# Catatan kecil di bawahnya
st.markdown(
    f"""
    <p style='text-align:center; color:{TEXT_GRAY}; font-size:12px; margin-top:10px;'>
        Semakin tinggi nilai volatilitas, semakin besar potensi risiko dan peluang dalam pergerakan harga saham.
    </p>
    """,
    unsafe_allow_html=True
)

# =========================================================
# Catatan akhir
# =========================================================
st.markdown(
    f"""
    <p style='text-align:center; color:{TEXT_GRAY}; font-size:12px; margin-top:5px;'>
        Gunakan data volatilitas bersama hasil prediksi harga untuk strategi investasi yang lebih seimbang.
    </p>
    """,
    unsafe_allow_html=True
)

def weight_to_label_color(weight):
    if weight > 0:
        return "UP", "#00C853"
    elif weight < 0:
        return "DOWN", "#FF4B4B"
    else:
        return "NETRAL", "#FFB300"

# ======================================
# Jika ada hasil LIME (contributions)
# ======================================
if "lime_contrib" in st.session_state and st.session_state.lime_contrib:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<h4 style='color:white; text-align:center;'>Hasil Pembobotan Kata (LIME)</h4>",
        unsafe_allow_html=True
    )

    for word, weight in st.session_state.lime_contrib:
        label, warna = weight_to_label_color(weight)

        st.markdown(
            f"""
<div style='
    display:flex;
    justify-content:center;
    align-items:center;
    margin-bottom:8px;
    gap:12px;
'>
    <!-- kata -->
    <div style='
        font-size:18px;
        color:{TEXT_LIGHT};
        min-width:180px;
        text-align:right;
        padding:6px 14px;
        border-radius:999px;
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.06);
    '>
        {word}
    </div>
</div>

<div style='
    display:flex;
    justify-content:center;
    align-items:center;
    margin-bottom:8px;
    gap:12px;
'>
    <!-- label + bobot -->
    <div style='
        font-size:13px;
        font-weight:bold;
        color:{warna};
        text-align:left;
        padding:4px 10px;
        border-radius:999px;
        background:rgba(0,0,0,0.5);
        border:1px solid {warna};
    '>
        {label} · {weight:.4f}
    </div>
</div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 🔙 Tombol Kembali ke Homepage
# =========================================================
st.markdown("<hr style='border: 0.5px solid #333;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

if st.button("⬅ Kembali ke Homepage"):
    try:
        st.switch_page("../app.py")  # Streamlit v1.25+
    except:
        st.info("Navigasi ke homepage tidak tersedia di mode ini. Jalankan dengan multipage layout Streamlit.")

st.markdown("</div>", unsafe_allow_html=True)
