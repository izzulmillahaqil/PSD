import json
import folium
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

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
    " **Sentinel-2A** dan algoritma **Decision Tree Classifier**."
)


# ---------------------------------------------------------
# 2. Load Dataset & GeoJSON
# ---------------------------------------------------------
@st.cache_data
def load_data():
  # Load CSV Sampel Titik
  df = pd.read_csv("dataset_sentinel2_jatim.csv")
  df["kelas"] = df["kelas"].astype(str).str.strip()
  pemetaan_kelas = {"Air": "Laut", "Water": "Laut", "Laut/Air": "Laut"}
  df["kelas"] = df["kelas"].replace(pemetaan_kelas)

  # Load GeoJSON Polygon
  try:
    with open("LLLC_Jawa_Timur_Fix.json", "r") as f:
      geojson_data = json.load(f)
  except Exception:
    geojson_data = None

  return df, geojson_data


try:
  df_sampel, geojson_data = load_data()
except Exception as e:
  st.error(f"Gagal memuat dataset: {e}")
  df_sampel, geojson_data = None, None

# ---------------------------------------------------------
# 3. Sidebar Input Nilai Spektral
# ---------------------------------------------------------
st.sidebar.header("🎛️ Input Nilai Spektral Sentinel-2A")

b2 = st.sidebar.slider("B2 - Blue", 0.0, 1.0, 0.05)
b3 = st.sidebar.slider("B3 - Green", 0.0, 1.0, 0.08)
b4 = st.sidebar.slider("B4 - Red", 0.0, 1.0, 0.06)
b8 = st.sidebar.slider("B8 - NIR", 0.0, 1.0, 0.45)
b11 = st.sidebar.slider("B11 - SWIR1", 0.0, 1.0, 0.16)
b12 = st.sidebar.slider("B12 - SWIR2", 0.0, 1.0, 0.10)

ndvi = (b8 - b4) / (b8 + b4) if (b8 + b4) != 0 else 0
ndwi = (b3 - b8) / (b3 + b8) if (b3 + b8) != 0 else 0
ndbi = (b11 - b8) / (b11 + b8) if (b11 + b8) != 0 else 0
mndwi = (b3 - b11) / (b3 + b11) if (b3 + b11) != 0 else 0
savi = ((b8 - b4) / (b8 + b4 + 0.5)) * 1.5 if (b8 + b4 + 0.5) != 0 else 0
bsi = ((b11 + b4) - (b8 + b2)) / ((b11 + b4) + (b8 + b2)) if ((b11 + b4) + (b8 + b2)) != 0 else 0

col1, col2 = st.columns([1, 1])

with col1:
  st.subheader("📊 Hasil Kalkulasi Indeks Spektral")
  st.write("Nilai indeks dari parameter input:")
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
# 4. Peta Spasial Folium (Persis seperti notebook .ipynb)
# ---------------------------------------------------------
with col2:
  st.subheader("🗺️ Peta Klasifikasi LULC Jawa Timur")

  AOI_JATIM = [111.0, -8.85, 114.65, -6.75]
  pusat_peta = [
      (AOI_JATIM[1] + AOI_JATIM[3]) / 2,
      (AOI_JATIM[0] + AOI_JATIM[2]) / 2,
  ]

  NAMA_KELAS = ["Sawah", "Bangunan", "Mangrove", "Lahan Hijau", "Laut", "Danau"]
  WARNA_KELAS = {
      "Sawah": "#EAD86F",
      "Bangunan": "#D85E5E",
      "Mangrove": "#A578C0",
      "Lahan Hijau": "#6EA06B",
      "Laut": "#5380C0",
      "Danau": "#7CD2F1",
  }

  m = folium.Map(location=pusat_peta, zoom_start=8, control_scale=True)

  # Google Hybrid Layer
  folium.TileLayer(
      tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
      attr="Google Hybrid Satellite",
      name="Google Hybrid (Satelit + Label)",
      max_zoom=20,
      overlay=False,
  ).add_to(m)

  # Polygon GeoJSON Layer
  if geojson_data:
    grup_geojson = folium.FeatureGroup(name="Polygon GeoJSON", show=True)
    folium.GeoJson(
        geojson_data,
        style_function=lambda f: {
            "fillColor": WARNA_KELAS.get(
                f.get("properties", {}).get("kelas", "Danau"), "#7CD2F1"
            ),
            "color": "white",
            "weight": 1.2,
            "fillOpacity": 0.4,
        },
    ).add_to(grup_geojson)
    grup_geojson.add_to(m)

  # Titik-Titik Sampel dari CSV
  if df_sampel is not None:
    if "prediksi" not in df_sampel.columns:
      df_sampel["prediksi"] = df_sampel["kelas"]
    if "evaluasi" not in df_sampel.columns:
      df_sampel["evaluasi"] = np.where(
          df_sampel["kelas"] == df_sampel["prediksi"], "Tepat", "Meleset"
      )

    for nama in NAMA_KELAS:
      sub = df_sampel[df_sampel["kelas"] == nama]
      grup = folium.FeatureGroup(
          name=f"Sampel: {nama} ({len(sub)} Titik)", show=True
      )

      for _, r in sub.iterrows():
        if pd.isna(r["lat"]) or pd.isna(r["lon"]):
          continue
        warna_titik = WARNA_KELAS.get(nama, "#3388ff")

        popup_html = f"""
                <div style='font-family: Arial, sans-serif; font-size: 11px; width: 200px;'>
                    <b style='color:{warna_titik}; font-size: 13px;'>{nama}</b><br>
                    <b>Koordinat:</b> {r["lon"]:.4f} BT, {r["lat"]:.4f} LS
                </div>
                """
        folium.CircleMarker(
            [r["lat"], r["lon"]],
            radius=5.5,
            color="white",
            weight=1.2,
            fill=True,
            fill_color=warna_titik,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=220),
        ).add_to(grup)
      grup.add_to(m)

  # Batas BBox Jatim
  grup_aoi = folium.FeatureGroup(
      name="Batas Area Studi (BBox Jatim)", show=True
  )
  folium.Rectangle(
      [[AOI_JATIM[1], AOI_JATIM[0]], [AOI_JATIM[3], AOI_JATIM[2]]],
      color="yellow",
      weight=1.8,
      fill=False,
      dash_array="6",
  ).add_to(grup_aoi)
  grup_aoi.add_to(m)

  # Legenda HTML
  items_legenda = "".join(
      f'<div style="margin:3px 0;"><span'
      f' style="display:inline-block;width:12px;height:12px;background:{WARNA_KELAS[k]};border:1px'
      " solid"
      ' #333;margin-right:6px;border-radius:50%;"></span>{k}</div>'
      for k in NAMA_KELAS
  )

  legenda_html = f"""
    <div style="position:fixed; bottom:30px; left:20px; z-index:9999; background:white;
         padding:8px 12px; border:2px solid #555; border-radius:6px; font:11px Arial;
         box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    <b>Legenda Tutupan Lahan</b><br><hr style="margin:3px 0;">
    {items_legenda}
    </div>
    """
  m.get_root().html.add_child(folium.Element(legenda_html))

  folium.LayerControl(position="topright", collapsed=False).add_to(m)

  st_folium(m, width="100%", height=550)