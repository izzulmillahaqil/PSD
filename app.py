import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. Konfigurasi Halaman Web
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sistem Informasi LULC Jawa Timur",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Sistem Informasi Land Use & Land Cover (LULC) Jawa Timur")
st.write(
    "Aplikasi klasifikasi tutupan lahan **6 Kelas** (Sawah, Bangunan, Danau, Lahan Hijau, Laut, Mangrove) "
    "berbasis citra satelit **Sentinel-2A** dan algoritma **Decision Tree Classifier**, "
    "dilengkapi visualisasi peta interaktif **Google Maps Satellite**."
)

# ---------------------------------------------------------
# 2. Load Model Machine Learning
# ---------------------------------------------------------
@st.cache_resource
def load_model():
    return joblib.load('model_lulc.pkl')

try:
    model = load_model()
    st.sidebar.success("✅ Model ML Berhasil Dimuat!")
except Exception as e:
    st.sidebar.error(f"❌ Gagal memuat model: {e}")

# ---------------------------------------------------------
# 3. Sidebar Input Nilai Spektral (Bands & Fitur)
# ---------------------------------------------------------
st.sidebar.header("🎛️ Input Nilai Spektral Sentinel-2A")
st.sidebar.write("Simulasikan nilai reflektansi permukaan untuk menguji prediksi Decision Tree:")

b2 = st.sidebar.slider("B2 - Blue (0.490 µm)", 0.0, 1.0, 0.05)
b3 = st.sidebar.slider("B3 - Green (0.560 µm)", 0.0, 1.0, 0.08)
b4 = st.sidebar.slider("B4 - Red (0.665 µm)", 0.0, 1.0, 0.06)
b8 = st.sidebar.slider("B8 - NIR (0.842 µm)", 0.0, 1.0, 0.45)
b11 = st.sidebar.slider("B11 - SWIR1 (1.610 µm)", 0.0, 1.0, 0.16)
b12 = st.sidebar.slider("B12 - SWIR2 (2.190 µm)", 0.0, 1.0, 0.10)

# Kalkulasi Indeks Spektral Otomatis
ndvi = (b8 - b4) / (b8 + b4) if (b8 + b4) != 0 else 0
ndwi = (b3 - b8) / (b3 + b8) if (b3 + b8) != 0 else 0
ndbi = (b11 - b8) / (b11 + b8) if (b11 + b8) != 0 else 0
mndwi = (b3 - b11) / (b3 + b11) if (b3 + b11) != 0 else 0
savi = ((b8 - b4) / (b8 + b4 + 0.5)) * 1.5 if (b8 + b4 + 0.5) != 0 else 0
bsi = ((b11 + b4) - (b8 + b2)) / ((b11 + b4) + (b8 + b2)) if ((b11 + b4) + (b8 + b2)) != 0 else 0

# Layout Kolom Tampilan
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Hasil Prediksi Decision Tree")
    
    # Menyiapkan data input sesuai fitur saat training (B2, B3, B4, B8, B11, B12, NDVI, NDWI, NDBI, MNDWI)
    # Sesuaikan urutan ini jika data training Anda hanya memakai indeks spektral
    input_features = np.array([[b2, b3, b4, b8, b11, b12, ndvi, ndwi, ndbi, mndwi]])
    
    try:
        prediksi = model.predict(input_features)[0]
        st.markdown(f"### Kelas Terdeteksi: **{prediksi}**")
    except Exception as e:
        # Fallback jika model hanya menerima 4/8 indeks
        try:
            input_indices = np.array([[ndvi, ndwi, mndwi, ndbi]])
            prediksi = model.predict(input_indices)[0]
            st.markdown(f"### Kelas Terdeteksi: **{prediksi}**")
        except Exception as err:
            st.error(f"Sesuaikan jumlah fitur input dengan model: {err}")

    st.markdown("---")
    st.write("#### Indeks Spektral Terkalkulasi:")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("NDVI (Vegetasi)", f"{ndvi:.3f}")
        st.metric("NDBI (Bangunan)", f"{ndbi:.3f}")
        st.metric("SAVI (Koreksi Tanah)", f"{savi:.3f}")
    with col_b:
        st.metric("NDWI (Badan Air)", f"{ndwi:.3f}")
        st.metric("MNDWI (Air Modifikasi)", f"{mndwi:.3f}")
        st.metric("BSI (Tanah Terbuka)", f"{bsi:.3f}")

# ---------------------------------------------------------
# 4. Peta Spasial Folium (Google Maps Satellite Default)
# ---------------------------------------------------------
with col2:
    st.subheader("🗺️ Peta Klasifikasi LULC Jawa Timur")
    
    # 1. Objek Peta dikunci pada koordinat Jawa Timur (-7.5360, 112.2384) dengan zoom pas (8)
    m = folium.Map(
        location=[-7.5360, 112.2384],
        zoom_start=8,
        tiles=None  # Kosongkan basemap bawaan OpenStreetMap
    )

    # 2. Layer Utama: Google Maps Satellite (Default Aktif)
    google_sat = folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Google Satellite',
        overlay=False
    ).add_to(m)

    # 3. Layer Alternatif: Google Maps Roadmap
    google_map = folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google Roadmap',
        name='Google Maps Roadmap',
        overlay=False
    ).add_to(m)

    # 4. Kontrol Layer Peta
    folium.LayerControl(position='topright').add_to(m)

    # 5. Render Peta di Streamlit
    st_folium(m, width=650, height=520)