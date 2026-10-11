import geopandas as gpd
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium

# ---------------------------------------------------------
# 1. Konfigurasi Halaman Web
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sistem Informasi LULC Jawa Timur",
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 Sistem Informasi Land Use & Land Cover (LULC) Jawa Timur")
st.write(
    "Aplikasi klasifikasi tutupan lahan **6 Kelas** berbasis citra satelit"
    " **Sentinel-2A** dan algoritma **Decision Tree Classifier**, dilengkapi"
    " visualisasi peta interaktif **Google Maps Satellite**."
)


# ---------------------------------------------------------
# 2. Load Model ML & Data GeoJSON
# ---------------------------------------------------------
@st.cache_resource
def load_model():
  return joblib.load("model_lulc.pkl")


@st.cache_data
def load_geojson(path):
  gdf = gpd.read_file(path)
  if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)
  return gdf


try:
  model = load_model()
  st.sidebar.success("✅ Model ML Berhasil Dimuat!")
except Exception as e:
  st.sidebar.error(f"❌ Gagal memuat model: {e}")

try:
  gdf = load_geojson("LLLC_Jawa_Timur_Fix.json")
except Exception as e:
  st.error(f"Gagal memuat GeoJSON: {e}")
  gdf = None

# ---------------------------------------------------------
# 3. Sidebar Input Nilai Spektral
# ---------------------------------------------------------
st.sidebar.header("🎛️ Input Nilai Spektral Sentinel-2A")

b2 = st.sidebar.slider("B2 - Blue (0.490 µm)", 0.0, 1.0, 0.05)
b3 = st.sidebar.slider("B3 - Green (0.560 µm)", 0.0, 1.0, 0.08)
b4 = st.sidebar.slider("B4 - Red (0.665 µm)", 0.0, 1.0, 0.06)
b8 = st.sidebar.slider("B8 - NIR (0.842 µm)", 0.0, 1.0, 0.45)
b11 = st.sidebar.slider("B11 - SWIR1 (1.610 µm)", 0.0, 1.0, 0.16)
b12 = st.sidebar.slider("B12 - SWIR2 (2.190 µm)", 0.0, 1.0, 0.10)

# Kalkulasi Indeks Spektral
ndvi = (b8 - b4) / (b8 + b4) if (b8 + b4) != 0 else 0
ndwi = (b3 - b8) / (b3 + b8) if (b3 + b8) != 0 else 0
ndbi = (b11 - b8) / (b11 + b8) if (b11 + b8) != 0 else 0
mndwi = (b3 - b11) / (b3 + b11) if (b3 + b11) != 0 else 0
savi = ((b8 - b4) / (b8 + b4 + 0.5)) * 1.5 if (b8 + b4 + 0.5) != 0 else 0
bsi = ((b11 + b4) - (b8 + b2)) / ((b11 + b4) + (b8 + b2)) if ((b11 + b4) + (b8 + b2)) != 0 else 0

col1, col2 = st.columns([1, 1])

with col1:
  st.subheader("📊 Hasil Prediksi Decision Tree")

  # Menyesuaikan 18 Fitur Input untuk Model Decision Tree
  input_18 = np.array([[
      b2,
      b3,
      b4,
      b8,
      b11,
      b12,
      ndvi,
      ndwi,
      ndbi,
      mndwi,
      savi,
      bsi,
      b8 - b4,
      b3 - b8,
      b11 - b8,
      b3 - b11,
      b2 / (b8 + 1e-5),
      b4 / (b8 + 1e-5),
  ]])

  try:
    prediksi = model.predict(input_18)[0]
    st.markdown(f"### Kelas Terdeteksi: **{prediksi}**")
  except Exception as e:
    st.error(f"Gagal memprediksi: {e}")

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
# 4. Peta Spasial Folium (Persis Web Referensi)
# ---------------------------------------------------------
with col2:
  st.subheader("🗺️ Peta Klasifikasi LULC Jawa Timur")

  # Inisialisasi Peta
  m = folium.Map(location=[-7.5360, 112.2384], zoom_start=8, control_scale=True)

  # Google Hybrid Satellite Base Layer
  folium.TileLayer(
      tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
      attr="Google Hybrid Satellite",
      name="Google Hybrid (Satelit + Label)",
      overlay=False,
  ).add_to(m)

  # Esri World Imagery
  folium.TileLayer(
      tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      attr="Tiles &copy; Esri",
      name="Esri Satellite",
      overlay=False,
      show=False,
  ).add_to(m)

  WARNA_KELAS = {
      "Sawah": "#EAD86F",
      "Bangunan": "#D85E5E",
      "Mangrove": "#A578C0",
      "Lahan Hijau": "#6EA06B",
      "Laut": "#5380C0",
      "Danau": "#7CD2F1",
  }

  if gdf is not None:
    # Cari nama kolom kelas secara dinamis
    kolom_kelas = next(
        (
            col
            for col in gdf.columns
            if col.lower() in ["kelas", "class", "lulc", "label"]
        ),
        gdf.columns[0],
    )

    # Render GeoJSON Polygon Layer
    folium.GeoJson(
        gdf,
        name="Polygon GeoJSON",
        style_function=lambda feature: {
            "fillColor": WARNA_KELAS.get(
                str(feature["properties"].get(kolom_kelas, "")).strip().title(),
                "#7CD2F1",
            ),
            "color": "white",
            "weight": 1.2,
            "fillOpacity": 0.5,
        },
        popup=folium.GeoJsonPopup(
            fields=[kolom_kelas], aliases=["Kelas LULC:"], localize=True
        ),
    ).add_to(m)

  # Menambahkan Legenda Kartografi HTML Melayang di Kiri Bawah Peta
  legenda_items = "".join(
      f'<div style="margin:2px 0;"><span'
      f' style="display:inline-block;width:12px;height:12px;background:{warna};border:1px'
      " solid"
      ' #333;margin-right:6px;border-radius:50%;"></span>{kelas}</div>'
      for kelas, warna in WARNA_KELAS.items()
  )

  legenda_html = f"""
    <div style="position: fixed; bottom: 30px; left: 20px; width: 160px; z-index:9999; 
                background-color: white; padding: 10px; border: 2px solid grey; 
                border-radius: 5px; font-size: 11px; font-family: sans-serif;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <b>Legenda Tutupan Lahan</b><br>
        <small>Sentinel-2A LULC</small><hr style="margin:3px 0;">
        {legenda_items}
    </div>
    """
  m.get_root().html.add_child(folium.Element(legenda_html))

  folium.LayerControl(position="topright", collapsed=False).add_to(m)

  # Render Peta
  st_folium(m, width="100%", height=530)