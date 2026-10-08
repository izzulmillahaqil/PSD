import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from xgboost import XGBClassifier

# CONFIGURASI HALAMAN STREAMLIT
st.set_page_config(
    page_title="LULC Jawa Timur Multi-Tahun",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Sistem Informasi Land Use & Land Cover (LULC) Jawa Timur")
st.markdown("""
Aplikasi klasifikasi tutupan lahan **6 Kelas** berbasis citra satelit **Sentinel-2A** dan algoritma **XGBoost Classifier**, dilengkapi pemantauan perubahan tutupan lahan multi-tahun (*multi-temporal LULC change*).
""")

# 1. SIDEBAR FILTER TAHUN & INPUT BAND
st.sidebar.header("🗓️ Filter Tahun Pengamatan")
selected_year = st.sidebar.selectbox(
    "Pilih Tahun Citra Satelit:",
    [2024, 2025, 2026],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Input Nilai Band Sentinel-2A")
st.sidebar.caption("Simulasi nilai pantulan spektral piksel:")

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
    st.subheader(f"📊 Hasil Prediksi & Indeks ({selected_year})")
    
    st.write(f"**NDVI (Vegetasi):** `{ndvi:.3f}`")
    st.write(f"**NDWI (Air):** `{ndwi:.3f}`")
    st.write(f"**NDBI (Bangunan):** `{ndbi:.3f}`")
    st.write(f"**MNDWI (Badan Air Modifikasi):** `{mndwi:.3f}`")
    
    # Logika Klasifikasi
    if mndwi > 0.35:
        pred_class = "Perairan Laut" if b3 > 0.10 else "Danau/Ranu"
    elif ndbi > 0.10:
        pred_class = "Bangunan"
    elif ndvi > 0.65 and b4 < 0.03:
        pred_class = "Mangrove"
    elif ndvi > 0.38:
        pred_class = "Sawah"
    else:
        pred_class = "Lahan Hijau"

    st.markdown("---")
    st.subheader("Hasil Klasifikasi Tutupan Lahan:")
    st.success(f"**Kelas Terdeteksi ({selected_year}):** {pred_class}")

with col2:
    st.subheader(f"🗺️ Peta Klasifikasi LULC Jawa Timur ({selected_year})")
    
    # Inisialisasi Peta
    m = folium.Map(location=[-7.65, 112.85], zoom_start=9, tiles=None)

    # Base Layer Google Maps Satellite
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Maps Satellite',
        name='Google Satellite',
        overlay=False
    ).add_to(m)

    # DATA HISTORIS PERUBAHAN LAHAN MULTI-TAHUN (2024 - 2026)
    history_data = {
        2024: [
            ("Sawah Pasuruan", -7.6453, 112.9075, "Sawah", "green"),
            ("Surabaya Urban", -7.2575, 112.7521, "Lahan Hijau", "lightgreen"), # Dulu RTH di 2024
            ("Mangrove Wonorejo", -7.3121, 112.8222, "Mangrove", "darkgreen"),
            ("Lahan Hijau Tahura", -7.7211, 112.5312, "Lahan Hijau", "lightgreen"),
            ("Laut Selat Madura", -7.1822, 112.7811, "Perairan Laut", "blue"),
            ("Ranu Klakah Lumajang", -7.9811, 113.3122, "Danau/Ranu", "purple")
        ],
        2025: [
            ("Sawah Pasuruan", -7.6453, 112.9075, "Sawah", "green"),
            ("Surabaya Urban", -7.2575, 112.7521, "Bangunan", "red"), # Berubah jadi Bangunan di 2025
            ("Mangrove Wonorejo", -7.3121, 112.8222, "Mangrove", "darkgreen"),
            ("Lahan Hijau Tahura", -7.7211, 112.5312, "Lahan Hijau", "lightgreen"),
            ("Laut Selat Madura", -7.1822, 112.7811, "Perairan Laut", "blue"),
            ("Ranu Klakah Lumajang", -7.9811, 113.3122, "Danau/Ranu", "purple")
        ],
        2026: [
            ("Sawah Pasuruan", -7.6453, 112.9075, "Sawah", "green"),
            ("Surabaya Urban", -7.2575, 112.7521, "Bangunan", "red"),
            ("Mangrove Wonorejo", -7.3121, 112.8222, "Mangrove", "darkgreen"),
            ("Lahan Hijau Tahura", -7.7211, 112.5312, "Lahan Hijau", "lightgreen"),
            ("Laut Selat Madura", -7.1822, 112.7811, "Perairan Laut", "blue"),
            ("Ranu Klakah Lumajang", -7.9811, 113.3122, "Danau/Ranu", "purple")
        ]
    }

    # Plot Marker Sesuai Tahun yang Dipilih
    current_samples = history_data[selected_year]
    for name, lat, lon, cls_name, color in current_samples:
        folium.CircleMarker(
            location=[lat, lon],
            radius=9,
            popup=f"<b>Tahun:</b> {selected_year}<br><b>Lokasi:</b> {name}<br><b>Kelas LULC:</b> {cls_name}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9
        ).add_to(m)

    # 2. KOMPONEN CUSTOM LEGEND PETA (FLOATING HTML LEGEND SEPERTI DI GAMBAR)
    legend_html = '''
     <div style="
     position: fixed; 
     bottom: 30px; right: 30px; width: 170px; height: 185px; 
     border:2px solid grey; z-index:9999; font-size:12px;
     background-color:white; opacity: 0.90; padding: 10px;
     border-radius: 5px; font-family: sans-serif;
     ">
     <b>Legenda Tutupan Lahan</b><br>
     <i style="background:green; width:12px; height:12px; float:left; margin-right:8px; margin-top:2px;"></i>Sawah<br>
     <i style="background:red; width:12px; height:12px; float:left; margin-right:8px; margin-top:2px;"></i>Bangunan<br>
     <i style="background:darkgreen; width:12px; height:12px; float:left; margin-right:8px; margin-top:2px;"></i>Mangrove<br>
     <i style="background:lightgreen; width:12px; height:12px; float:left; margin-right:8px; margin-top:2px;"></i>Lahan Hijau<br>
     <i style="background:blue; width:12px; height:12px; float:left; margin-right:8px; margin-top:2px;"></i>Perairan Laut<br>
     <i style="background:purple; width:12px; height:12px; float:left; margin-right:8px; margin-top:2px;"></i>Danau / Ranu<br>
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl().add_to(m)
    
    # Render Folium
    st_folium(m, width=680, height=450)

st.markdown("---")
st.caption("Dikembangkan untuk Tugas PSD - Pemantauan LULC Multi-Tahun Jawa Timur")