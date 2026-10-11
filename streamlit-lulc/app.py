import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
from streamlit_folium import st_folium

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Klasifikasi LULC Jawa Timur",
    layout="wide"
)

st.title("🌱 Aplikasi Klasifikasi Tutupan Lahan (LULC) Jawa Timur")
st.write("Aplikasi prediksi tutupan lahan menggunakan model Machine Learning dan Citra Sentinel-2A.")

# Load Model
@st.cache_resource
def load_model():
    return joblib.load('model_lulc.pkl')

try:
    model = load_model()
    st.sidebar.success("Model ML Berhasil Dimuat!")
except Exception as e:
    st.sidebar.error(f"Gagal memuat model: {e}")

# Sidebar Input Nilai
st.sidebar.header("Input Fitur Prediksi")

# Catatan: Sesuaikan nama/jumlah input slider di bawah ini dengan fitur yang ada di FITUR_FINAL kamu
ndvi = st.sidebar.slider("NDVI", -1.0, 1.0, 0.4)
ndwi = st.sidebar.slider("NDWI", -1.0, 1.0, -0.2)
mndwi = st.sidebar.slider("MNDWI", -1.0, 1.0, -0.1)
ndbi = st.sidebar.slider("NDBI", -1.0, 1.0, 0.1)

if st.sidebar.button("Prediksi Tutupan Lahan"):
    # Array input sesuai urutan fitur model saat training
    input_data = np.array([[ndvi, ndwi, mndwi, ndbi]])
    try:
        prediksi = model.predict(input_data)[0]
        st.subheader("Hasil Klasifikasi:")
        st.success(f"Kategori LULC Terprediksi: **{prediksi}**")
    except Exception as e:
        st.error(f"Error saat prediksi: {e}")

# Tampilan Peta Spasial (Folium)
st.subheader("🗺️ Peta Wilayah Jawa Timur")
m = folium.Map(location=[-7.5360, 112.2384], zoom_start=8)

# Tambahkan layer Google Satellite
google_sat = folium.TileLayer(
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attr='Google Satellite',
    name='Google Satellite',
    overlay=False
)
google_sat.add_to(m)
folium.LayerControl().add_to(m)

# Tampilkan Peta
st_folium(m, width=900, height=500)