import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import io

st.set_page_config(page_title="Klasifikasi LULC Jatim", layout="wide")

KELAS = {
    1: dict(nama="Sawah", warna="#FFD92F"),
    2: dict(nama="Bangunan", warna="#E41A1C"),
    3: dict(nama="Mangrove", warna="#8E44AD"),
    4: dict(nama="Lahan Hijau", warna="#2E7D32"),
    5: dict(nama="Perairan Terbuka (Laut)", warna="#0D47A1"),
    6: dict(nama="Danau", warna="#4FC3F7"),
}
NAMA_KELAS = [v["nama"] for v in KELAS.values()]
WARNA_KELAS = {v["nama"]: v["warna"] for v in KELAS.values()}

def _nd(a, b):
    return (a - b) / (a + b + 1e-10)

@st.cache_data
def load_and_preprocess_data():
    df = pd.read_csv("dataset_sentinel2_jatim.csv")
    df["NDVI"] = _nd(df["B8"], df["B4"])
    df["NDWI"] = _nd(df["B3"], df["B8"])
    df["MNDWI"] = _nd(df["B3"], df["B11"])
    df["NDBI"] = _nd(df["B11"], df["B8"])
    df["NDRE"] = _nd(df["B8"], df["B5"])
    df["EVI"] = 2.5 * (df["B8"] - df["B4"]) / (df["B8"] + 6*df["B4"] - 7.5*df["B2"] + 1 + 1e-10)
    df["SAVI"] = (df["B8"] - df["B4"]) * 1.5 / (df["B8"] + df["B4"] + 0.5 + 1e-10)
    df["BSI"] = _nd(df["B11"] + df["B4"], df["B8"] + df["B2"])
    return df

st.title("Klasifikasi Penggunaan Lahan (LULC) Jawa Timur")
st.markdown("Menggunakan Citra Sentinel-2A dan Machine Learning Decision Tree.")

try:
    df = load_and_preprocess_data()
except FileNotFoundError:
    st.error("File dataset_sentinel2_jatim.csv tidak ditemukan.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["Eksplorasi Data", "Peta Spasial", "Model Decision Tree", "Prediksi Data Baru"])

with tab1:
    st.subheader("Distribusi Jumlah Sampel per Kelas")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(df["kelas"].value_counts().reset_index().rename(columns={"kelas": "Kelas", "count": "Jumlah Sampel"}))
        st.write(f"Total Data: {len(df)} sampel")
    with col2:
        jml = df["kelas"].value_counts().reindex(NAMA_KELAS)
        st.bar_chart(jml, color="#2E7D32")
    st.subheader("Cuplikan Dataset")
    st.dataframe(df.head())

with tab2:
    st.subheader("Peta Persebaran Titik Sampel Jawa Timur")
    # PERUBAHAN 1: Tiles diubah menjadi OpenStreetMap untuk menghilangkan watermark 'API KEY REQUIRED'
    m = folium.Map(location=[-7.9, 112.9], zoom_start=7, tiles="OpenStreetMap")
    
    for idx, row in df.iterrows():
        # PERUBAHAN 2: Deteksi lokasi di luar Jatim (Kasar: Lat di luar -8.9 s/d -6.5 atau Lon di luar 111.0 s/d 114.6)
        # Angka ini adalah perkiraan kotak (bounding box) Provinsi Jawa Timur
        if row["lat"] < -8.9 or row["lat"] > -6.5 or row["lon"] < 111.0 or row["lon"] > 114.6:
            warna = "black"
            tooltip_teks = f"⚠️ SALAH KLASIFIKASI (Di luar Jatim!) | {row['kelas']} (Lat: {row['lat']:.3f}, Lon: {row['lon']:.3f})"
        else:
            warna = WARNA_KELAS.get(row["kelas"], "gray")
            tooltip_teks = f"{row['kelas']} (Lat: {row['lat']:.3f}, Lon: {row['lon']:.3f})"
            
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5, color=warna, fill=True, fill_color=warna, fill_opacity=0.8,
            tooltip=tooltip_teks
        ).add_to(m)
        
    st_folium(m, width=900, height=500)

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
            nama_hasil = KELAS[prediksi]["nama"]
            warna_hasil = KELAS[prediksi]["warna"]
            
            st.markdown(f"### Hasil Prediksi: <span style='color:{warna_hasil}'>{nama_hasil}</span>", unsafe_allow_html=True)
            with st.expander("Lihat Data Input Lengkap (Band + Indeks)"):
                st.dataframe(data_baru)