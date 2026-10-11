import streamlit as st
import pandas as pd
import numpy as np
import folium
import json
import io
import joblib
from streamlit_folium import st_folium
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Konfigurasi Halaman
st.set_page_config(page_title="Klasifikasi LULC Jatim", layout="wide")

# Penyelarasan Variabel Kelas dan Warna
NAMA_KELAS = ["Sawah", "Bangunan", "Mangrove", "Lahan Hijau", "Laut", "Danau"]
WARNA_KELAS = {
    "Sawah": "#EAD86F",
    "Bangunan": "#D85E5E",
    "Mangrove": "#A578C0",
    "Lahan Hijau": "#6EA06B",
    "Laut": "#5380C0",
    "Danau": "#7CD2F1"
}

def _nd(a, b):
    return (a - b) / (a + b + 1e-10)

@st.cache_data
def load_and_preprocess_data():
    df = pd.read_csv("dataset_sentinel2_jatim.csv")
    
    # Ekstraksi Fitur / Indeks
    df["NDVI"] = _nd(df["B8"], df["B4"])
    df["NDWI"] = _nd(df["B3"], df["B8"])
    df["MNDWI"] = _nd(df["B3"], df["B11"])
    df["NDBI"] = _nd(df["B11"], df["B8"])
    df["NDRE"] = _nd(df["B8"], df["B5"])
    df["EVI"] = 2.5 * (df["B8"] - df["B4"]) / (df["B8"] + 6*df["B4"] - 7.5*df["B2"] + 1 + 1e-10)
    df["SAVI"] = (df["B8"] - df["B4"]) * 1.5 / (df["B8"] + df["B4"] + 0.5 + 1e-10)
    df["BSI"] = _nd(df["B11"] + df["B4"], df["B8"] + df["B2"])
    
    # Bersihkan nama kelas agar seragam
    df["kelas"] = df["kelas"].astype(str).str.strip()
    pemetaan_kelas = {
        "Air": "Laut",
        "Water": "Laut",
        "Laut/Air": "Laut",
        "Perairan Terbuka (Laut)": "Laut"
    }
    df["kelas"] = df["kelas"].replace(pemetaan_kelas)
    
    # Buka GeoJSON
    with open("LLLC_Jawa_Timur_Fix.geojson", "r") as f:
        geojson_data = json.load(f)
        
    return df, geojson_data

# --- HEADER APP ---
st.title("Klasifikasi Penggunaan Lahan (LULC) Jawa Timur")
st.markdown("Menggunakan Citra Sentinel-2A dan Machine Learning Decision Tree.")

try:
    df, geojson_data = load_and_preprocess_data()
except FileNotFoundError:
    st.error("File dataset_sentinel2_jatim.csv atau LLLC_Jawa_Timur_Fix.geojson tidak ditemukan.")
    st.stop()

# --- SIDEBAR (Khusus filter Peta) ---
st.sidebar.header("Filter Peta (Tab 2)")
pilih_kelas = st.sidebar.multiselect("Pilih Kelas Tutupan Lahan:", NAMA_KELAS, default=NAMA_KELAS)

# --- MENU TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["Eksplorasi Data", "Peta Spasial", "Model Decision Tree", "Prediksi Data Baru"])

# --- TAB 1: EKSPLORASI DATA ---
with tab1:
    st.subheader("Distribusi Jumlah Sampel per Kelas")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(df["kelas"].value_counts().reset_index().rename(columns={"kelas": "Kelas", "count": "Jumlah Sampel"}))
        st.write(f"Total Data: {len(df)} sampel")
    with col2:
        jml = df["kelas"].value_counts().reindex(NAMA_KELAS).fillna(0)
        st.bar_chart(jml, color="#2E7D32")
    st.subheader("Cuplikan Dataset")
    st.dataframe(df.head())


# --- TAB 2: PETA SPASIAL ADVANCED ---
with tab2:
    st.subheader("Peta Persebaran Titik Sampel Jawa Timur")
    
    AOI_JATIM = [111.0, -8.85, 114.65, -6.75]
    pusat_peta = [(AOI_JATIM[1] + AOI_JATIM[3]) / 2, (AOI_JATIM[0] + AOI_JATIM[2]) / 2]
    
    if "prediksi" not in df.columns:
        df["prediksi"] = df["kelas"]
    if "evaluasi" not in df.columns:
        df["evaluasi"] = np.where(df["kelas"] == df["prediksi"], "Tepat", "Meleset")

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

    # Polygon GeoJSON
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

    # Render Titik Sampel (Berdasarkan Sidebar Filter)
    df_filtered = df[df["kelas"].isin(pilih_kelas)]
    for nama in pilih_kelas:
        sub = df_filtered[df_filtered["kelas"] == nama]
        if len(sub) == 0:
            continue
            
        grup = folium.FeatureGroup(name=f"Sampel: {nama} ({len(sub)} Titik)", show=True)
        for _, r in sub.iterrows():
            popup_html = f"""
            <div style='font-family: Arial, sans-serif; font-size: 11px; width: 220px;'>
                <b style='color:{WARNA_KELAS[nama]}; font-size: 13px;'>{nama}</b><br>
                <b>Status Prediksi:</b> <span style='color:{"green" if r["evaluasi"]=="Tepat" else "red"}'><b>{r["evaluasi"]}</b></span><br>
                <b>Hasil Model:</b> {r["prediksi"]}<br>
                <b>Koordinat:</b> {r["lon"]:.4f} BT, {r["lat"]:.4f} LS<br>
                <hr style='margin:4px 0;'>
                <b>NDVI:</b> {r.get("NDVI", 0):.3f} | <b>NDWI:</b> {r.get("NDWI", 0):.3f}<br>
                <b>MNDWI:</b> {r.get("MNDWI", 0):.3f} | <b>NDBI:</b> {r.get("NDBI", 0):.3f}
            </div>
            """
            folium.CircleMarker(
                [r.lat, r.lon],
                radius=5.5,
                color="white",
                weight=1.2,
                fill=True,
                fill_color=WARNA_KELAS[nama],
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

    # Menampilkan ke Streamlit Tab
    st_folium(peta, width=1100, height=600, key="map_jatim_main")


# --- TAB 3: MODEL DECISION TREE ---
with tab3:
    st.subheader("Training & Evaluasi Model")
    FITUR = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12', 
             'NDVI', 'NDWI', 'MNDWI', 'NDBI', 'NDRE', 'EVI', 'SAVI', 'BSI']
    X = df[FITUR]
    y = df["kelas"]
    
    test_size = st.slider("Proporsi Data Uji (Test Size)", 0.1, 0.5, 0.3, 0.1)
    
    if st.button("Latih & Evaluasi Model"):
        with st.spinner("Membangun pohon keputusan..."):
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            model = DecisionTreeClassifier(random_state=42)
            model.fit(X_train, y_train)
            
            st.session_state['model_dt'] = model
            st.session_state['akurasi'] = accuracy_score(y_test, model.predict(X_test))
            st.session_state['report'] = pd.DataFrame(classification_report(y_test, model.predict(X_test), output_dict=True)).transpose()

    if 'model_dt' in st.session_state:
        st.success("Model berhasil dilatih!")
        st.metric("Akurasi Model", f"{st.session_state['akurasi'] * 100:.2f}%")
        st.dataframe(st.session_state['report'].style.format("{:.3f}"))
        
        model_bytes = io.BytesIO()
        joblib.dump(st.session_state['model_dt'], model_bytes)
        model_bytes.seek(0)
        st.download_button("Unduh Model (.pkl)", data=model_bytes, file_name="model_lulc.pkl", mime="application/octet-stream")


# --- TAB 4: PREDIKSI DATA BARU ---
with tab4:
    st.subheader("Prediksi Lahan dari Nilai Citra Baru")
    
    if 'model_dt' not in st.session_state:
        st.warning("Silakan latih model terlebih dahulu di tab 'Model Decision Tree' sebelum melakukan prediksi.")
    else:
        st.markdown("Masukkan nilai reflektansi (pantulan) dari 10 Band Sentinel-2A:")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            b2 = st.number_input("B2 (Blue)", value=0.120)
            b3 = st.number_input("B3 (Green)", value=0.150)
            b4 = st.number_input("B4 (Red)", value=0.110)
            b5 = st.number_input("B5 (Red Edge 1)", value=0.140)
        with c2:
            b6 = st.number_input("B6 (Red Edge 2)", value=0.250)
            b7 = st.number_input("B7 (Red Edge 3)", value=0.300)
            b8 = st.number_input("B8 (NIR)", value=0.350)
            b8a = st.number_input("B8A (Narrow NIR)", value=0.360)
        with c3:
            b11 = st.number_input("B11 (SWIR 1)", value=0.200)
            b12 = st.number_input("B12 (SWIR 2)", value=0.150)
            
        if st.button("Prediksi Kelas Lahan"):
            ndvi = _nd(b8, b4)
            ndwi = _nd(b3, b8)
            mndwi = _nd(b3, b11)
            ndbi = _nd(b11, b8)
            ndre = _nd(b8, b5)
            evi = 2.5 * (b8 - b4) / (b8 + 6*b4 - 7.5*b2 + 1 + 1e-10)
            savi = (b8 - b4) * 1.5 / (b8 + b4 + 0.5 + 1e-10)
            bsi = _nd(b11 + b4, b8 + b2)
            
            data_baru = pd.DataFrame([[
                b2, b3, b4, b5, b6, b7, b8, b8a, b11, b12,
                ndvi, ndwi, mndwi, ndbi, ndre, evi, savi, bsi
            ]], columns=FITUR)
            
            prediksi = st.session_state['model_dt'].predict(data_baru)[0]
            warna_hasil = WARNA_KELAS.get(prediksi, "#000000")
            
            st.markdown(f"### Hasil Prediksi: <span style='color:{warna_hasil}'>{prediksi}</span>", unsafe_allow_html=True)
            with st.expander("Lihat Data Input Lengkap (Band + Indeks)"):
                st.dataframe(data_baru)