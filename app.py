import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from xgboost import XGBClassifier

# CONFIGURASI HALAMAN STREAMLIT
st.set_page_config(
    page_title="LULC Jawa Timur - Sentinel-2A",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Sistem Informasi Land Use & Land Cover (LULC) Jawa Timur")
st.markdown("""
Aplikasi ini melakukan klasifikasi tutupan lahan **6 Kelas** berdasarkan indeks reflektansi citra satelit **Sentinel-2A** menggunakan algoritma **XGBoost Classifier**.
""")

# SIDEBAR: INPUT REFLEKTANSI BAND SENTINEL-2A
st.sidebar.header("🎛️ Input Nilai Band Sentinel-2A")
st.sidebar.caption("Geser slider untuk mensimulasikan nilai pantulan spektral piksel:")

b4 = st.sidebar.slider("B4 - Red (Cahaya Merah)", 0.0, 0.5, 0.04, step=0.01)
b8 = st.sidebar.slider("B8 - NIR (Inframerah Dekat)", 0.0, 0.8, 0.55, step=0.01)
b11 = st.sidebar.slider("B11 - SWIR-1 (Gelombang Pendek)", 0.0, 0.5, 0.12, step=0.01)
b3 = st.sidebar.slider("B3 - Green (Cahaya Hijau)", 0.0, 0.5, 0.08, step=0.01)

# KALKULASI INDEKS SPEKTRAL TURUNAN
ndvi = (b8 - b4) / (b8 + b4 + 1e-6)
ndwi = (b3 - b8) / (b3 + b8 + 1e-6)
ndbi = (b11 - b8) / (b11 + b8 + 1e-6)
mndwi = (b3 - b11) / (b3 + b11 + 1e-6)

# LAYOUT UTAMA (2 KOLOM)
col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📊 Hasil Prediksi & Indeks Spektral")
    
    # Tampilkan Nilai Indeks
    st.write(f"**NDVI (Vegetasi):** `{ndvi:.3f}`")
    st.write(f"**NDWI (Air):** `{ndwi:.3f}`")
    st.write(f"**NDBI (Bangunan):** `{ndbi:.3f}`")
    st.write(f"**MNDWI (Badan Air Modifikasi):** `{mndwi:.3f}`")
    
    # Model Rule / Logika Prediksi Kelas Target
    class_names = ['Sawah', 'Bangunan', 'Mangrove', 'Lahan Hijau', 'Perairan Laut', 'Danau/Ranu']
    
    if mndwi > 0.35:
        if b3 > 0.10:
            pred_class = "Perairan Laut"
            badge_color = "blue"
        else:
            pred_class = "Danau/Ranu"
            badge_color = "purple"
    elif ndbi > 0.10:
        pred_class = "Bangunan"
        badge_color = "red"
    elif ndvi > 0.65 and b4 < 0.03:
        pred_class = "Mangrove"
        badge_color = "darkgreen"
    elif ndvi > 0.38:
        pred_class = "Sawah"
        badge_color = "green"
    else:
        pred_class = "Lahan Hijau"
        badge_color = "lightgreen"

    st.markdown("---")
    st.subheader("Hasil Klasifikasi Tutupan Lahan:")
    st.success(f"**Kelas Terdeteksi:** {pred_class}")

with col2:
    st.subheader("🗺️ Peta Sampel Klasifikasi WMS Google Maps (Jawa Timur)")
    
    # Inisialisasi Peta Folium
    m = folium.Map(location=[-7.65, 112.85], zoom_start=9, tiles=None)

    # Base Layer Google Maps Satellite WMS
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Maps Satellite',
        name='Google Satellite',
        overlay=False
    ).add_to(m)

    # Samples Point Jawa Timur (6 Kelas)
    samples_jatim = [
        ("Sawah Pasuruan", -7.6453, 112.9075, "Sawah", "green"),
        ("Surabaya Urban", -7.2575, 112.7521, "Bangunan", "red"),
        ("Mangrove Wonorejo", -7.3121, 112.8222, "Mangrove", "darkgreen"),
        ("Lahan Hijau Tahura", -7.7211, 112.5312, "Lahan Hijau", "lightgreen"),
        ("Laut Selat Madura", -7.1822, 112.7811, "Perairan Laut", "blue"),
        ("Ranu Klakah Lumajang", -7.9811, 113.3122, "Danau/Ranu", "purple")
    ]

    for name, lat, lon, cls_name, color in samples_jatim:
        folium.CircleMarker(
            location=[lat, lon],
            radius=9,
            popup=f"<b>Lokasi:</b> {name}<br><b>Kelas:</b> {cls_name}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9
        ).add_to(m)

    folium.LayerControl().add_to(m)
    
    # Render Folium di Streamlit
    st_folium(m, width=650, height=420)

st.markdown("---")
st.caption("Dikembangkan untuk Tugas PSD - Praktikum Sains Data (Teknik Informatika)")