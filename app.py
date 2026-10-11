import streamlit as st
import folium
import json
import pandas as pd
import numpy as np
from streamlit_folium import st_folium

# Konfigurasi Halaman Streamlit (Harus paling atas)
st.set_page_config(page_title="Dashboard LULC Jawa Timur", layout="wide")

st.title("Klasifikasi Penggunaan dan Tutupan Lahan Jawa Timur")
st.write("Dashboard interaktif pemodelan tutupan lahan menggunakan data Sentinel-2 dan Python Folium.")

# Membuat Menu Tab seperti di gambar Anda
tab1, tab2, tab3, tab4 = st.tabs(["Eksplorasi Data", "Peta Spasial", "Model Decision Tree", "Prediksi Data Baru"])

# 1. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("dataset_sentinel2_jatim.csv")
    with open("LLLC_Jawa_Timur_Fix.geojson", "r") as f:
        geojson_data = json.load(f)
    return df, geojson_data

df, geojson_data = load_data()

# Bersihkan spasi tak sengaja pada nilai string di kolom kelas
df["kelas"] = df["kelas"].astype(str).str.strip()

pemetaan_kelas = {
    "Air": "Laut",
    "Water": "Laut",
    "Laut/Air": "Laut"
}
df["kelas"] = df["kelas"].replace(pemetaan_kelas)

# Pastikan kolom prediksi & evaluasi ada
if "prediksi" not in df.columns:
    df["prediksi"] = df["kelas"]

if "evaluasi" not in df.columns:
    df["evaluasi"] = np.where(df["kelas"] == df["prediksi"], "Tepat", "Meleset")

AOI_JATIM = [111.0, -8.85, 114.65, -6.75]
pusat_peta = [(AOI_JATIM[1] + AOI_JATIM[3]) / 2, (AOI_JATIM[0] + AOI_JATIM[2]) / 2]

NAMA_KELAS = ["Sawah", "Bangunan", "Mangrove", "Lahan Hijau", "Laut", "Danau"]
WARNA_KELAS = {
    "Sawah": "#EAD86F",
    "Bangunan": "#D85E5E",
    "Mangrove": "#A578C0",
    "Lahan Hijau": "#6EA06B",
    "Laut": "#5380C0",
    "Danau": "#7CD2F1"
}

# --- SIDEBAR GLOBAL ---
st.sidebar.header("Filter Peta")
pilih_kelas = st.sidebar.multiselect("Pilih Kelas Tutupan Lahan:", NAMA_KELAS, default=NAMA_KELAS)
filter_status = st.sidebar.selectbox("Filter Status Evaluasi:", ["Semua Titik", "Hanya yang Tepat", "Hanya yang Meleset (Salah)"])


# --- ISI TAB 2: PETA SPASIAL ---
with tab2:
    st.header("Peta Persebaran Titik Sampel Jawa Timur")
    
    peta = folium.Map(location=pusat_peta, zoom_start=8, tiles=None, control_scale=True)

    # Base Layers
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google Hybrid Satellite",
        name="Google Hybrid (Satelit + Label)",
        max_zoom=20,
        overlay=False,
        control=True,
    ).add_to(peta)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
        name="Esri Satellite",
        max_zoom=19,
        overlay=False,
        control=True,
        show=False
    ).add_to(peta)

    # Render Polygon GeoJSON
    grup_geojson = folium.FeatureGroup(name="Polygon GeoJSON", show=True)
    folium.GeoJson(
        geojson_data,
        style_function=lambda f: {
            "fillColor": WARNA_KELAS.get(f.get("properties", {}).get("kelas"), "#888888"),
            "color": "white",
            "weight": 1.2,
            "fillOpacity": 0.5,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["kelas"] if len(geojson_data["features"]) > 0 and "kelas" in geojson_data["features"][0]["properties"] else [],
            aliases=["Kelas:"],
            localize=True
        )
    ).add_to(grup_geojson)
    grup_geojson.add_to(peta)

    # Filter dataframe berdasarkan pilihan sidebar
    df_filtered = df[df["kelas"].isin(pilih_kelas)]
    if filter_status == "Hanya yang Tepat":
        df_filtered = df_filtered[df_filtered["evaluasi"] == "Tepat"]
    elif filter_status == "Hanya yang Meleset (Salah)":
        df_filtered = df_filtered[df_filtered["evaluasi"] == "Meleset"]

    # Render Titik Sampel dengan penanda khusus jika Meleset
    for nama in pilih_kelas:
        sub = df_filtered[df_filtered["kelas"] == nama]
        if len(sub) == 0:
            continue
            
        grup = folium.FeatureGroup(name=f"Sampel: {nama} ({len(sub)} Titik)", show=True)
        for _, r in sub.iterrows():
            is_meleset = (r["evaluasi"] == "Meleset")
            
            # Pengaturan visual jika salah prediksi: garis tepi hitam tebal & ukuran sedikit lebih besar
            marker_color = "#FF0000" if is_meleset else WARNA_KELAS[nama]
            border_color = "#000000" if is_meleset else "white"
            border_weight = 2.5 if is_meleset else 1.2
            radius_size = 6.5 if is_meleset else 5.5

            popup_html = f"""
            <div style='font-family: Arial, sans-serif; font-size: 11px; width: 220px;'>
                <b style='color:{WARNA_KELAS[nama]}; font-size: 13px;'>{nama}</b><br>
                <b>Status Prediksi:</b> <span style='color:{"green" if not is_meleset else "red"}'><b>{r["evaluasi"]}</b></span><br>
                <b>Hasil Model:</b> {r["prediksi"]}<br>
                <b>Koordinat:</b> {r["lon"]:.4f} BT, {r["lat"]:.4f} LS<br>
                <hr style='margin:4px 0;'>
                <b>NDVI:</b> {r.get("NDVI", 0):.3f} | <b>NDWI:</b> {r.get("NDWI", 0):.3f}<br>
                <b>MNDWI:</b> {r.get("MNDWI", 0):.3f} | <b>NDBI:</b> {r.get("NDBI", 0):.3f}
            </div>
            """
            
            folium.CircleMarker(
                [r.lat, r.lon],
                radius=radius_size,
                color=border_color,
                weight=border_weight,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.9,
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(grup)
        grup.add_to(peta)

    # Batas AOI
    grup_aoi = folium.FeatureGroup(name="Batas Area Studi (BBox Jatim)", show=True)
    folium.Rectangle(
        [[AOI_JATIM[1], AOI_JATIM[0]], [AOI_JATIM[3], AOI_JATIM[2]]],
        color="yellow", weight=1.8, fill=False, dash_array="6"
    ).add_to(grup_aoi)
    grup_aoi.add_to(peta)

    folium.LayerControl(collapsed=False).add_to(peta)

    # Tampilkan Peta ke dalam Streamlit tepat di dalam Tab 2
    st_folium(peta, width=1100, height=600, key="peta_jatim")

# (Opsional) Isi untuk tab lainnya agar tidak kosong
with tab1:
    st.write("Konten Eksplorasi Data Anda di sini.")
with tab3:
    st.write("Konten Model Decision Tree Anda di sini.")
with tab4:
    st.write("Konten Prediksi Data Baru Anda di sini.")