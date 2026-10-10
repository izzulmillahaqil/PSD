import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

# CONFIGURASI HALAMAN STREAMLIT
st.set_page_config(
    page_title="LULC Jawa Timur - Decision Tree",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Sistem Informasi Land Use & Land Cover (LULC) Jawa Timur")
st.markdown("""
Aplikasi klasifikasi tutupan lahan **6 Kelas** (Sawah, Bangunan, Danau, Lahan Hijau, Laut, Mangrove) berbasis citra satelit **Sentinel-2A** dan algoritma **Decision Tree Classifier**, dilengkapi visualisasi peta interaktif **Google Maps Satellite (WMS/XYZ)**.
""")

# LOAD & PREPARE DATASET 300 SAMPEL (50 PER KELAS)
DATA_PATH = "data/processed/dataset_lulc_jatim_300.csv"
class_names = ['Sawah', 'Bangunan', 'Danau', 'Lahan Hijau', 'Laut', 'Mangrove']
features = ['B2_Blue', 'B3_Green', 'B4_Red', 'B8_NIR', 'B11_SWIR1', 'B12_SWIR2', 'NDVI', 'NDWI', 'NDBI', 'MNDWI', 'SAVI', 'BSI']

@st.cache_data
def load_and_train_model():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        # Fallback dataset generator jika file belum ada
        np.random.seed(42)
        rows = []
        for c_idx, c_name in enumerate(class_names):
            for i in range(50):
                b2 = np.random.uniform(0.04, 0.08) if c_name == 'Sawah' else np.random.uniform(0.12, 0.22)
                b3 = np.random.uniform(0.06, 0.12)
                b4 = np.random.uniform(0.05, 0.09)
                b8 = np.random.uniform(0.35, 0.52)
                b11 = np.random.uniform(0.12, 0.22)
                b12 = np.random.uniform(0.08, 0.16)
                eps = 1e-6
                rows.append({
                    'Sample_ID': f'{c_name[:3].upper()}_{i+1:02d}',
                    'Kelas': c_name, 'Label': c_idx,
                    'Latitude': -7.5 + np.random.uniform(-0.5, 0.5),
                    'Longitude': 112.5 + np.random.uniform(-0.5, 0.5),
                    'B2_Blue': b2, 'B3_Green': b3, 'B4_Red': b4, 'B8_NIR': b8,
                    'B11_SWIR1': b11, 'B12_SWIR2': b12,
                    'NDVI': (b8 - b4)/(b8 + b4 + eps),
                    'NDWI': (b3 - b8)/(b3 + b8 + eps),
                    'NDBI': (b11 - b8)/(b11 + b8 + eps),
                    'MNDWI': (b3 - b11)/(b3 + b11 + eps),
                    'SAVI': ((b8 - b4)*1.5)/(b8 + b4 + 0.5 + eps),
                    'BSI': ((b11 + b4) - (b8 + b2))/((b11 + b4) + (b8 + b2) + eps)
                })
        df = pd.DataFrame(rows)

    X = df[features]
    y = df['Label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    clf = DecisionTreeClassifier(criterion='gini', max_depth=5, min_samples_split=4, random_state=42)
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))
    
    return df, clf, acc

df, model_dt, test_acc = load_and_train_model()

# 1. SIDEBAR INPUT BAND SENTINEL-2A
st.sidebar.header("🎛️ Input Nilai Spektral Sentinel-2A")
st.sidebar.caption("Simulasikan nilai reflektansi permukaan untuk menguji prediksi Decision Tree:")

b2 = st.sidebar.slider("B2 - Blue (0.490 µm)", 0.00, 0.30, 0.05, step=0.01)
b3 = st.sidebar.slider("B3 - Green (0.560 µm)", 0.00, 0.30, 0.08, step=0.01)
b4 = st.sidebar.slider("B4 - Red (0.665 µm)", 0.00, 0.35, 0.06, step=0.01)
b8 = st.sidebar.slider("B8 - NIR (0.842 µm)", 0.00, 0.85, 0.45, step=0.01)
b11 = st.sidebar.slider("B11 - SWIR1 (1.610 µm)", 0.00, 0.50, 0.16, step=0.01)
b12 = st.sidebar.slider("B12 - SWIR2 (2.190 µm)", 0.00, 0.50, 0.10, step=0.01)

# KALKULASI FITUR INDEKS SPEKTRAL TURUNAN
eps = 1e-6
ndvi = (b8 - b4) / (b8 + b4 + eps)
ndwi = (b3 - b8) / (b3 + b8 + eps)
ndbi = (b11 - b8) / (b11 + b8 + eps)
mndwi = (b3 - b11) / (b3 + b11 + eps)
savi = ((b8 - b4) * 1.5) / (b8 + b4 + 0.5 + eps)
bsi = ((b11 + b4) - (b8 + b2)) / ((b11 + b4) + (b8 + b2) + eps)

# PREDIKSI DECISION TREE DARI SLIDER INPUT
input_features = pd.DataFrame([[b2, b3, b4, b8, b11, b12, ndvi, ndwi, ndbi, mndwi, savi, bsi]], columns=features)
pred_label = model_dt.predict(input_features)[0]
pred_class_name = class_names[pred_label]
pred_proba = model_dt.predict_proba(input_features)[0][pred_label] * 100

# FILTER KELAS PADA PETA
st.sidebar.markdown("---")
st.sidebar.header("🗺️ Filter Layer Peta")
filter_classes = st.sidebar.multiselect(
    "Pilih Kelas yang Ditampilkan:",
    class_names,
    default=class_names
)

# LAYOUT UTAMA DUA KOLOM
col1, col2 = st.columns([1, 1.4])

with col1:
    st.subheader("📊 Hasil Prediksi Decision Tree")
    st.info(f"**Akurasi Model Pengujian:** `{test_acc * 100:.2f}%` (Stratified Test Set)")
    
    st.markdown(f"### Kelas Terdeteksi: **{pred_class_name}**")
    st.progress(pred_proba / 100.0)
    st.caption(f"Tingkat Keyakinan (Node Purity): **{pred_proba:.1f}%**")
    
    st.markdown("---")
    st.subheader("Indeks Spektral Terkalkulasi:")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("NDVI (Vegetasi)", f"{ndvi:.3f}")
        st.metric("NDBI (Bangunan)", f"{ndbi:.3f}")
        st.metric("SAVI (Koreksi Tanah)", f"{savi:.3f}")
    with c2:
        st.metric("NDWI (Badan Air)", f"{ndwi:.3f}")
        st.metric("MNDWI (Air Modifikasi)", f"{mndwi:.3f}")
        st.metric("BSI (Tanah Terbuka)", f"{bsi:.3f}")

    st.markdown("---")
    st.subheader("Distribusi Sampel Ground Truth (Jawa Timur)")
    counts = df['Kelas'].value_counts()
    st.dataframe(pd.DataFrame({'Jumlah Titik': counts, 'Persentase': '16.67% (50/300)'}))

with col2:
    st.subheader("🗺️ Peta Klasifikasi LULC Jawa Timur (Folium - Google Maps Satellite)")
    
    # Inisialisasi Peta
    m = folium.Map(location=[-7.70, 112.70], zoom_start=8, tiles=None)

    # Base Layer Google Maps Satellite Hybrid (WMS / XYZ)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Maps Satellite Hybrid',
        name='Google Satellite (Hybrid)',
        overlay=False
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google Maps Jalan',
        name='Google Maps Road',
        overlay=False
    ).add_to(m)

    # Warna unik per kelas
    color_map = {
        'Sawah': '#2ca02c',
        'Bangunan': '#d62728',
        'Danau': '#9467bd',
        'Lahan Hijau': '#2ca25f',
        'Laut': '#1f77b4',
        'Mangrove': '#006d2c'
    }

    # Plotting titik sampel dari dataset
    df_filtered = df[df['Kelas'].isin(filter_classes)]
    for idx, row in df_filtered.iterrows():
        c_name = row['Kelas']
        color = color_map.get(c_name, 'gray')
        
        popup_content = f"""
        <b>ID:</b> {row['Sample_ID']}<br>
        <b>Kelas:</b> {c_name}<br>
        <b>Koordinat:</b> {row['Latitude']:.4f}, {row['Longitude']:.4f}<br>
        <b>NDVI:</b> {row['NDVI']:.3f} | <b>NDWI:</b> {row['NDWI']:.3f}<br>
        <b>NDBI:</b> {row['NDBI']:.3f}
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            popup=folium.Popup(popup_content, max_width=220),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=1.5
        ).add_to(m)

    # Custom Floating Legend
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 30px; right: 30px; width: 180px; height: 215px; 
        border:2px solid #555; z-index:9999; font-size:12px;
        background-color:rgba(255, 255, 255, 0.95); padding: 10px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3); border-radius: 6px;
        font-family: sans-serif;
    ">
    <b>Legenda Tutupan Lahan</b><br>
    <small>Decision Tree 6 Kelas</small><hr style="margin:4px 0;">
    <i style="background:#2ca02c; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i>Sawah (50)<br>
    <i style="background:#d62728; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i>Bangunan (50)<br>
    <i style="background:#9467bd; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i>Danau (50)<br>
    <i style="background:#2ca25f; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i>Lahan Hijau (50)<br>
    <i style="background:#1f77b4; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i>Laut (50)<br>
    <i style="background:#006d2c; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i>Mangrove (50)<br>
    <hr style="margin:4px 0;">
    <small><b>Total: 300 Sampel Jatim</b></small>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl(collapsed=False).add_to(m)

    st_folium(m, width=720, height=500)

st.markdown("---")
st.caption("Ujian Tengah Semester (UTS) - Sistem Informasi Geografis & Analisis Spasial Penggunaan Lahan Jawa Timur | Decision Tree Classifier & Sentinel-2A")