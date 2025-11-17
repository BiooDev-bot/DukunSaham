import streamlit as st
import datetime

# =====================
# 🧠 PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Stock Reaction Predictor",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =====================
# 🎨 CUSTOM STYLE (CSS)
# =====================
st.markdown("""
    <style>
        .main {
            background-color: #0e1117;
            color: white;
            font-family: 'Poppins', sans-serif;
        }
        h1 {
            font-size: 2.8em !important;
            font-weight: 700 !important;
            background: linear-gradient(90deg, #00c6ff, #0072ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            font-size: 1.2em;
            color: #d1d1d1;
            margin-top: -10px;
            margin-bottom: 40px;
        }
        .stButton>button {
            background: linear-gradient(90deg, #0072ff, #00c6ff);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6em 1.5em;
            font-size: 1.1em;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            background: linear-gradient(90deg, #00c6ff, #0072ff);
        }
        input, textarea {
            border-radius: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)

# =====================
# 🏠 HERO SECTION
# =====================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/128/4599/4599622.png", width=80)
with col2:
    st.markdown("<h1>News → Stock Reaction Predictor</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Prediksi bagaimana berita memengaruhi harga saham 📊</p>", unsafe_allow_html=True)

# =====================
# 📥 INPUT AREA
# =====================
headline = st.text_input("📰 Masukkan headline berita")
ticker = st.text_input("🏷️ Ticker (contoh: BBRI)")
price = st.number_input("💰 Harga sebelum berita", min_value=0.0)
tanggal = st.date_input(
    "📅 Tanggal berita",
    value=datetime.date.today(),  # default: hari ini
)

# Kalau mau dalam bentuk datetime (YYYY-MM-DD)
tanggal_datetime = datetime.datetime.combine(tanggal, datetime.time())

# =====================
# ⚙️ PREDICTION BUTTON
# =====================
if st.button("🔮 Prediksi"):
    # Placeholder hasil prediksi
    st.session_state["headline"] = headline
    st.session_state["ticker"] = ticker
    st.session_state["price"] = price
    st.session_state["tanggal"] = tanggal_datetime
    st.switch_page("pages/1_Analysis.py")

