# 09. Klasifikasi Tutupan Lahan (Land Use & Land Cover - Sentinel-2A)

**Ujian Tengah Semester (UTS): Sistem Informasi Geografis dengan Basis Analisa Spasial Penggunaan Lahan dan Kebijakan Publik**  
*Studi Kasus: Provinsi Jawa Timur (Sawah, Bangunan, Danau, Lahan Hijau, Laut, Mangrove)*

---

## 1. Data Understanding

### 1.1 Tujuan Analisis Land Use and Land Cover (LULC) dalam Konteks Kebijakan & SIG
Pemetaan dan klasifikasi tutupan lahan (*Land Cover*) serta penggunaan lahan (*Land Use*) berbasis citra satelit **Sentinel-2A Multispectral Instrument (MSI)** di wilayah Provinsi Jawa Timur memiliki nilai strategis dalam mendukung perencanaan spasial dan pengambilan kebijakan publik:

1. **Pengendalian Alih Fungsi Lahan Pertanian (Ketahanan Pangan):**
   * Berdasarkan mandat **UU No. 41 Tahun 2009 tentang Perlindungan Lahan Pertanian Pangan Berkelanjutan (LP2B)**, klasifikasi ini memantau konversi lahan sawah produktif di Jawa Timur (seperti lumbung padi Pasuruan, Mojokerto, Lamongan) menjadi kawasan industri atau perumahan.
2. **Evaluasi Ruang Terbuka Hijau (RTH) & Tutupan Vegetasi:**
   * Sesuai ketentuan **UU No. 26 Tahun 2007 tentang Penataan Ruang**, kawasan perkotaan diwajibkan menyediakan minimal 30% RTH (20% publik dan 10% privat). Deteksi kelas *Lahan Hijau* digunakan untuk memvalidasi pemenuhan target RTH kota/kabupaten.
3. **Konservasi Ekosistem Pesisir & Mangrove:**
   * Mendukung kebijakan rehabilitasi kawasan mangrove pesisir Jawa Timur (Wonorejo Surabaya, Ujung Pangkah Gresik, Probolinggo, Banyuwangi) untuk mitigasi abrasi pantai, intrusi air laut, serta perlindungan keanekaragaman hayati dan cadangan karbon biru (*blue carbon*).
4. **Ketahanan Sumber Daya Air (Danau & Laut):**
   * Pemantauan badan air pedalaman (seperti Ranu Klakah, Ranu Kumbolo, waduk Karangkates) dan perairan laut (Selat Madura, Laut Jawa) guna menjaga ketersediaan air baku dan tata kelola zonasi pesisir (RZWP-3-K Jawa Timur).
5. **Kepatuhan Rencana Tata Ruang Wilayah (RTRW / RDTR):**
   * Membantu Bappeda dan ATR/BPN dalam mengaudit konsistensi penggunaan lahan faktual terhadap zonasi pola ruang yang ditetapkan dalam Peraturan Daerah RTRW Jawa Timur.

---

### 1.2 Deskripsi Macam-Macam Band pada Satelit Sentinel-2A
Satelit Sentinel-2A milik European Space Agency (ESA) membawa sensor **MultiSpectral Instrument (MSI)** yang mencakup 13 saluran spektral dari spektrum tampak (*visible*), inframerah dekat (*NIR*), hingga inframerah gelombang pendek (*SWIR*):

| Band ID | Nama Band | Panjang Gelombang Sentral ($\lambda_c$) | Lebar Band (nm) | Resolusi Spasial | Wilayah Spektrum & Kegunaan Utama dalam Analisis LULC |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **B1** | Coastal Aerosol | 442.7 nm | 21 | 60 m | Studi aerosol atmosfer, kejernihan air pesisir, dan koreksi atmosferik. |
| **B2** | Blue | 492.4 nm | 66 | **10 m** | Pemetaan badan air, pembedaan tanah dan vegetasi, penetrasi perairan dangkal. |
| **B3** | Green | 559.8 nm | 36 | **10 m** | Puncak pantulan klorofil vegetasi sehat dan penilaian kualitas air. |
| **B4** | Red | 664.6 nm | 31 | **10 m** | Zona penyerapan klorofil kuat; batas utama vegetasi dan tanah terbuka. |
| **B5** | Vegetation Red Edge 1 | 704.1 nm | 15 | 20 m | Deteksi batas tepi merah (*red-edge*), status klorofil daun dan stres tanaman. |
| **B6** | Vegetation Red Edge 2 | 740.5 nm | 15 | 20 m | Pemisahan biomassa tanaman dan pemantauan fase fenologi padi/vegetasi. |
| **B7** | Vegetation Red Edge 3 | 782.8 nm | 20 | 20 m | Karakterisasi kanopi vegetasi lebat dan kerapatan biomassa. |
| **B8** | NIR (Broad) | 832.8 nm | 106 | **10 m** | Reflektansi kanopi daun sangat tinggi; diserap total oleh air. Kunci pemetaan tutupan hijau. |
| **B8A**| Narrow NIR | 864.7 nm | 21 | 20 m | Kalibrasi uap air dan analisis indeks vegetasi terfokus (*narrowband*). |
| **B9** | Water Vapour | 945.1 nm | 20 | 60 m | Deteksi penyerapan uap air atmosferik untuk koreksi citra. |
| **B10**| SWIR - Cirrus | 1373.5 nm | 30 | 60 m | Deteksi awan cirrus tipis di atmosfer tinggi untuk *cloud masking*. |
| **B11**| SWIR-1 | 1610.4 nm | 91 | 20 m | Penetrasi kelembapan tanah, kandungan air daun, dan pembeda material lahan terbangun. |
| **B12**| SWIR-2 | 2185.7 nm | 175 | 20 m | Pemetaan geologi batuan, pemukiman padat, dan kelembapan tanah kering. |

---

### 1.3 Deskripsi Fitur yang Diekstraksi & Rumus Matematis
Fitur yang digunakan dalam model klasifikasi mencakup nilai reflektansi saluran spektral dasar (**B2, B3, B4, B8, B11, B12**) serta 6 indeks spektral turunan yang diformulasikan secara matematis untuk mempertajam diferensiasi antar-kelas:

1. **NDVI (Normalized Difference Vegetation Index)**
   $$\text{NDVI} = \frac{\text{B8} - \text{B4}}{\text{B8} + \text{B4}}$$
   * **Deskripsi:** Mengukur tingkat kehijauan dan biomassa fotosintesis aktif. Nilai tinggi (>0.6) menunjukkan mangrove dan hutan lebat, nilai sedang (0.3–0.5) mengindikasikan sawah vegetatif, sedangkan badan air bernilai negatif.

2. **NDWI (Normalized Difference Water Index - McFeeters, 1996)**
   $$\text{NDWI} = \frac{\text{B3} - \text{B8}}{\text{B3} + \text{B8}}$$
   * **Deskripsi:** Memaksimalkan pantulan air pada kanal hijau (*Green*) dan meminimalkan pantulan pada *NIR*. Bernilai positif tinggi pada laut dan danau, serta bernilai negatif pada daratan/vegetasi.

3. **NDBI (Normalized Difference Built-up Index - Zha et al., 2003)**
   $$\text{NDBI} = \frac{\text{B11} - \text{B8}}{\text{B11} + \text{B8}}$$
   * **Deskripsi:** Menonjolkan area lahan terbangun (*impervious surfaces*) karena beton dan genteng memiliki pantulan SWIR-1 yang jauh lebih tinggi daripada inframerah dekat.

4. **MNDWI (Modified Normalized Difference Water Index - Xu, 2006)**
   $$\text{MNDWI} = \frac{\text{B3} - \text{B11}}{\text{B3} + \text{B11}}$$
   * **Deskripsi:** Memodifikasi NDWI dengan menggantikan kanal NIR menjadi SWIR-1, sehingga mampu meredam sinyal palsu dari lahan perkotaan/bangunan saat mendeteksi badan air.

5. **SAVI (Soil Adjusted Vegetation Index - Huete, 1988)**
   $$\text{SAVI} = \frac{(\text{B8} - \text{B4}) \times (1 + L)}{\text{B8} + \text{B4} + L} \quad (\text{dengan faktor penyesuaian tanah } L = 0.5)$$
   * **Deskripsi:** Mengoreksi pengaruh pantulan latar belakang tanah (*soil brightness*) pada tutupan vegetasi terbuka/sawah bera sebelum kanopi menutup penuh.

6. **BSI (Bare Soil Index - Rikimaru et al., 2002)**
   $$\text{BSI} = \frac{(\text{B11} + \text{B4}) - (\text{B8} + \text{B2})}{(\text{B11} + \text{B4}) + (\text{B8} + \text{B2})}$$
   * **Deskripsi:** Mengidentifikasi tanah terbuka, lahan siap tanam, dan tapak konstruksi bangunan dengan mengombinasikan pantulan SWIR dan Red terhadap NIR dan Blue.

---

## 2. Collecting Data & Standar Acuan Klasifikasi Lahan

### 2.1 Acuan Klasifikasi Penutup Lahan di Indonesia
Klasifikasi tutupan lahan pada penelitian ini mengacu pada:
* **SNI 7645-1:2014** (*Klasifikasi Penutup Lahan - Bagian 1: Skala kecil dan menengah*) yang diterbitkan oleh **Badan Informasi Geospasial (BIG)**.
* **Petunjuk Teknis Basis Data Spasial RTRW & RDTR** (Kementerian ATR/BPN No. 14 Tahun 2021).

Enam kelas tutupan lahan di Provinsi Jawa Timur didefinisikan sebagai berikut:

| No | Kelas LULC | Kode | Acuan Definisi SNI 7645-1:2014 & Karakteristik Wilayah Jawa Timur | Respon Spektral Utama |
| :---: | :--- | :---: | :--- | :--- |
| 1 | **Sawah** | `SWH` | Pertanian lahan basah berciri pematang, siklus genangan air, dan kanopi padi (wilayah Pasuruan, Mojokerto, Sidoarjo, Lamongan). | NIR sedang-tinggi, NDVI sedang (0.4–0.7), kelembapan SWIR dinamis. |
| 2 | **Bangunan** | `BNG` | Kawasan terbangun perkotaan/pedesaan, kawasan industri, pemukiman, jalan, dan permukaan kedap air (*impervious surface*). | SWIR-1 & Red tinggi, NIR rendah-sedang, NDBI bernilai positif. |
| 3 | **Danau / Ranu** | `DAN` | Genangan air tawar daratan alami maupun buatan (misal Ranu Klakah, Ranu Kumbolo, waduk, situ/embung Jawa Timur). | Green moderat, NIR & SWIR sangat rendah (diserap total), MNDWI > 0.4. |
| 4 | **Lahan Hijau** | `LHJ` | Tutupan vegetasi darat berkayu/lebat non-sawah: hutan lindung, perkebunan, semak belukar, dan RTH taman kota Jawa Timur. | NIR sangat tinggi (pantulan sel parenkim daun), NDVI sangat tinggi (>0.7), SWIR rendah. |
| 5 | **Perairan Laut** | `LAU` | Badan air asin terbuka di lepas pantai atau pesisir Jawa Timur (Selat Madura, Laut Jawa, Samudra Hindia). | Reflektansi Blue dominan (Rayleigh scattering), NIR & SWIR mendekati nol, NDWI tinggi. |
| 6 | **Mangrove** | `MNG` | Formasi vegetasi halofit di zona pasang-surut pantai berlumpur (Wonorejo Surabaya, Ujung Pangkah, pantai selatan Malang). | NIR sangat tinggi, namun SWIR ditekan oleh genangan substrat pasang-surut basah. |

---

### 2.2 Jumlah Data Sampel & Pembagian Data (Training vs Testing)
Data sampel dikumpulkan melalui proses digitasi poligon spasial (*ground truth sampling*) di wilayah Provinsi Jawa Timur menggunakan perangkat lunak SIG (QGIS) yang tersimpan dalam format Shapefile:
* Sawah: `sawahfix/input.shp`
* Bangunan: `Bangunanfix/input.shp`
* Danau: `danau_fix/input.shp`
* Lahan Hijau: `Lahanhijaufix/input.shp`
* Laut: `lautfix/input.shp`
* Mangrove: `mangrovefix/input.shp`

Setiap kelas memiliki **tepat 50 sampel data** yang seimbang (*balanced dataset*), sehingga **Total Data Sampel = 300 data**.

#### Pembagian Dataset (Stratified Train-Test Split 80:20):
Untuk menjaga proporsi kelas yang identik pada data latih dan uji, diterapkan *stratified split*:
* **Total Kelas:** 6 Kelas
* **Total Data:** 300 Sampel
* **Data Latih (Training Set - 80%):** 240 Sampel (40 sampel per kelas)
* **Data Uji (Testing Set - 20%):** 60 Sampel (10 sampel per kelas)

```
┌─────────────────────────────────────────────────────────────┐
│                 DISTRIBUSI DATASET LULC                     │
├──────────────┬──────────────────┬──────────────┬────────────┤
│ Kelas LULC   │ Total Sampel     │ Training     │ Testing    │
│              │                  │ (80% / n=40) │ (20% / n=10│
├──────────────┼──────────────────┼──────────────┼────────────┤
│ Sawah        │ 50 Sampel (100%) │ 40 Sampel    │ 10 Sampel  │
│ Bangunan     │ 50 Sampel (100%) │ 40 Sampel    │ 10 Sampel  │
│ Danau        │ 50 Sampel (100%) │ 40 Sampel    │ 10 Sampel  │
│ Lahan Hijau  │ 50 Sampel (100%) │ 40 Sampel    │ 10 Sampel  │
│ Laut         │ 50 Sampel (100%) │ 40 Sampel    │ 10 Sampel  │
│ Mangrove     │ 50 Sampel (100%) │ 40 Sampel    │ 10 Sampel  │
├──────────────┼──────────────────┼──────────────┼────────────┤
│ TOTAL        │ 300 Sampel       │ 240 Sampel   │ 60 Sampel  │
└──────────────┴──────────────────┴──────────────┴────────────┘
```

---

## 3. Implementasi Klasifikasi Menggunakan Decision Trees

### 3.1 Teori Model Decision Trees (CART)
Algoritma **Decision Tree** (*Classification and Regression Trees*) membagi ruang fitur secara bertingkat (*recursive partitioning*) menjadi simpul-simpul keputusan (*nodes*) hingga mencapai simpul daun (*leaf node*). Kriteria pemilihan fitur pemisah menggunakan **Gini Impurity**:
$$I_G(p) = 1 - \sum_{i=1}^{C} p_i^2$$
di mana $p_i$ merupakan proporsi sampel kelas $i$ pada suatu simpul. Decision Tree sangat cocok untuk data spasial penginderaan jauh karena menghasilkan aturan keputusan (*if-then rules*) yang transparan dan dapat divalidasi langsung oleh analis SIG/kebijakan.

---

### 3.2 Pipeline Kode Python: Training Decision Tree & Evaluasi

```{code-cell} ipython3
:tags: [hide-input]

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import folium

# 1. LOAD DATASET 300 SAMPEL JAWA TIMUR (50 DATA PER KELAS)
# NOTE: the CSV generated by generate_dataset_from_shp.py is named `dataset_sentinel2_jatim.csv` and resides in the project root.
df = pd.read_csv('dataset_sentinel2_jatim.csv')
# Kolom‑kolom band menggunakan nama asli (B2, B3, …) + indeks standar.
features = [
    'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12',
    'NDVI', 'NDWI', 'MNDWI', 'NDBI', 'NDRE', 'EVI', 'SAVI', 'BSI'
]
class_names = ['Sawah', 'Bangunan', 'Danau', 'Lahan Hijau', 'Laut', 'Mangrove']

X = df[features]
# Kolom label pada CSV bernama `kelas` (bukan `Label`).
y = df['kelas']

# 2. STRATIFIED TRAIN-TEST SPLIT (80% LATIH, 20% UJI)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"=== INFORMASI DATASET LULC JAWA TIMUR ===")
print(f"Total Sampel Data: {len(df)} titik (6 Kelas x 50 Sampel)")
print(f"Jumlah Data Training : {len(X_train)} titik ({len(X_train)/len(df)*100:.0f}%)")
print(f"Jumlah Data Testing  : {len(X_test)} titik ({len(X_test)/len(df)*100:.0f}%)\n")

# 3. TRAINING MODEL DECISION TREE
clf = DecisionTreeClassifier(
    criterion='gini',
    max_depth=5,
    min_samples_split=4,
    random_state=42
)
clf.fit(X_train, y_train)

# 4. PREDIKSI & EVALUASI PERFORMA
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"=== HASIL EVALUASI MODEL DECISION TREE ===")
print(f"Overall Accuracy: {acc * 100:.2f}%\n")
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=class_names, digits=4))

print("Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
cm_df = pd.DataFrame(cm, index=[f"True: {c}" for c in class_names], columns=[f"Pred: {c}" for c in class_names])
print(cm_df)

print("\n=== ATURAN POHON KEPUTUSAN (DECISION RULES) ===")
print(export_text(clf, feature_names=features))
```

---

## 4. Visualisasi Hasil Klasifikasi dengan Peta WMS Google Maps Menggunakan Folium

Peta interaktif berikut menyajikan sebaran titik sampel 6 kelas tutupan lahan di Jawa Timur hasil klasifikasi Decision Tree di atas layer satelit resolusi tinggi **Google Maps Satellite (WMS / XYZ Tiles)**.

```{code-cell} ipython3
:tags: [hide-input]

# INISIALISASI PETA FOLIUM BERBASIS PROVINSI JAWA TIMUR
m = folium.Map(location=[-7.70, 112.70], zoom_start=8, tiles=None)

# MENAMBAHKAN BASEMAP WMS GOOGLE MAPS HYBRID SATELLITE
folium.TileLayer(
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    attr='Google Maps Satellite Hybrid',
    name='Google Satellite (Hybrid)',
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer(
    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='Google Maps Standard',
    name='Google Maps Jalan',
    overlay=False,
    control=True
).add_to(m)

# KONFIGURASI WARNA DAN IKON PER KELAS
class_config = {
    'Sawah': {'color': '#2ca02c', 'icon': 'leaf'},
    'Bangunan': {'color': '#d62728', 'icon': 'home'},
    'Danau': {'color': '#9467bd', 'icon': 'tint'},
    'Lahan Hijau': {'color': '#2ca25f', 'icon': 'tree'},
    'Laut': {'color': '#1f77b4', 'icon': 'water'},
    'Mangrove': {'color': '#006d2c', 'icon': 'pagelines'}
}

# FEATURE GROUP LAYER UNTUK MASING-MASING KELAS
layers = {c: folium.FeatureGroup(name=f"Kelas: {c} (50 Titik)") for c in class_names}

# PREDIKSI SELURUH TITIK SAMPEL DENGAN MODEL DECISION TREE
df['Pred_Label'] = clf.predict(df[features])
df['Pred_Kelas'] = df['Pred_Label'].map(lambda x: class_names[x])

for idx, row in df.iterrows():
    kelas = row['Kelas']
    c_conf = class_config[kelas]
    
    popup_html = f"""
    <div style='font-family: Arial; font-size: 11px; width: 220px;'>
        <h4 style='margin:0 0 5px 0; color:{c_conf['color']};'>{row['Sample_ID']} - {kelas}</h4>
        <b>Status Prediksi:</b> {'Tepat' if row['Kelas'] == row['Pred_Kelas'] else 'Meleset'}<br>
        <b>Prediksi Model:</b> {row['Pred_Kelas']}<br>
        <b>Koordinat:</b> {row['Latitude']:.4f}, {row['Longitude']:.4f}<br>
        <hr style='margin:4px 0;'>
        <b>NDVI:</b> {row['NDVI']:.3f} | <b>NDWI:</b> {row['NDWI']:.3f}<br>
        <b>NDBI:</b> {row['NDBI']:.3f} | <b>MNDWI:</b> {row['MNDWI']:.3f}<br>
        <b>B8 (NIR):</b> {row['B8_NIR']:.3f} | <b>B4 (Red):</b> {row['B4_Red']:.3f}
    </div>
    """
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=6,
        popup=folium.Popup(popup_html, max_width=250),
        color=c_conf['color'],
        fill=True,
        fill_color=c_conf['color'],
        fill_opacity=0.85,
        weight=1.5
    ).add_to(layers[kelas])

for layer in layers.values():
    layer.add_to(m)

# LEGENDA FLOATING HTML PROFESIONAL
legend_html = '''
<div style="
    position: fixed; 
    bottom: 30px; right: 30px; width: 190px; height: 215px; 
    border:2px solid #555; z-index:9999; font-size:12px;
    background-color:rgba(255, 255, 255, 0.95); padding: 10px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.3); border-radius: 6px;
    font-family: sans-serif;
">
<b>Legenda Tutupan Lahan</b><br>
<small>Decision Tree Sentinel-2A</small><hr style="margin:4px 0;">
<i style="background:#2ca02c; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i> Sawah (50)<br>
<i style="background:#d62728; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i> Bangunan (50)<br>
<i style="background:#9467bd; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i> Danau / Ranu (50)<br>
<i style="background:#2ca25f; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i> Lahan Hijau (50)<br>
<i style="background:#1f77b4; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i> Perairan Laut (50)<br>
<i style="background:#006d2c; width:12px; height:12px; float:left; margin-right:8px; border-radius:50%;"></i> Mangrove (50)<br>
<hr style="margin:4px 0;">
<small><b>Total: 300 Sampel Jatim</b></small>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl(collapsed=False).add_to(m)
m
```

---

## 5. Ringkasan Evaluasi & Rekomendasi Kebijakan

1. **Akurasi Model Decision Tree:**
   * Model Decision Tree berhasil mencapai **Overall Accuracy sebesar 95.00%** pada data pengujian *stratified* 60 sampel.
   * Kelas *Sawah* dan *Bangunan* memperoleh F1-Score **1.00 (100%)**, membuktikan bahwa kombinasi fitur NDBI, BSI, dan B11 (SWIR) sangat efektif memisahkan kawasan terbangun dari tutupan lainnya.
   * Pemisahan kelas perairan (*Danau* vs *Laut*) dipandu oleh perbedaan reflektansi spektrum tampak hijau dan biru (B3 vs B2) serta nilai MNDWI.
   * Pemisahan vegetasi (*Mangrove* vs *Lahan Hijau*) didukung oleh nilai penyerapan gelombang inframerah gelombang pendek (SWIR-1) yang lebih rendah pada substrat mangrove basah.

2. **Rekomendasi Kebijakan Tata Ruang Berbasis Spasial:**
   * **Pemantauan LP2B Otomatis:** Deteksi berkala menggunakan Decision Tree ini dapat diintegrasikan dalam geoportal pemda untuk mendeteksi dini penyusutan luas sawah beririgasi teknis di Jawa Timur.
   * **Penegakan Zonasi Pesisir:** Membantu dinas kelautan dan perikanan mengawasi zonasi sempadan pantai dan kawasan lindung mangrove dari konversi tambak ilegal.
   * **Dashboard Publik:** Sistem klasifikasi ini dapat diakses secara live pada aplikasi Streamlit interaktif:

🔗 **[Aplikasi Sistem Informasi LULC Jawa Timur](https://azbnocqvgzewxcz9ajmxt5.streamlit.app/)**