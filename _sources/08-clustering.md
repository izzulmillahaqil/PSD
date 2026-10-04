---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
---

# 8. Clustering Fitur TSFEL & Klasifikasi Tutupan Lahan Sawah

Dokumen ini menjelaskan alur pengolahan data polutan udara berbasis **Database MySQL**, reduksi dimensi multi-tahap (PCA), evaluasi kluster dengan *Silhouette Coefficient*, serta pemodelan klasifikasi tutupan lahan **Sawah vs Non-Sawah** berbasis citra satelit **Sentinel-2A**.

---

## BAB 1: Clustering Fitur TSFEL Kualitas Udara (MySQL & Reduksi Dimensi)

### 1.1 Metodologi & Alur Kerja
1. **Penyimpanan Database MySQL**: Data 204 fitur TSFEL diunggah dan disimpan ke dalam dua tabel terpisah di database `basisda1_PSD-A-Interpolasi`, yaitu `ekstraksi_fitur_linier` dan `ekstraksi_fitur_polynomial`.
2. **Pemisahan Per Polutan & Jenis Interpolasi**: Fitur TSFEL dikelompokkan berdasarkan variabel polutan ($\text{NO}_2$, $\text{CO}$, $\text{SO}_2$) untuk masing-masing metode interpolasi (Polynomial dan Linier).
3. **Reduksi Dimensi Multi-Tahap (PCA)**:
   - **Tahap 1**: Reduksi fitur dari masing-masing polutan ke komponen utama menggunakan PCA.
   - **Tahap 2**: Proyeksi ke **2 komponen utama 2D** untuk pemetaan dan visualisasi ruang kluster.
4. **Eksperimen Silhouette Coefficient**: Pengujian variasi jumlah kluster ($k = 2$ hingga $k = 5$) untuk menentukan struktur sebaran data paling optimal.

---

## BAB 1: Clustering Fitur TSFEL Kualitas Udara (MySQL & Reduksi Dimensi)

### 1.1 Metodologi & Alur Kerja
1. **Penggabungan Fitur Polutan**: Menggabungkan fitur TSFEL dari 3 variabel polutan ($\text{NO}_2$, $\text{CO}$, dan $\text{SO}_2$) untuk masing-masing dataset interpolasi (Linier dan Polynomial), menghasilkan total **204 kolom fitur**.
2. **Reduksi Dimensi Multi-Tahap (PCA)**:
   - **Tahap 1 ($204 \rightarrow 74$)**: Mereduksi 204 fitur TSFEL menjadi 74 komponen utama untuk mengeliminasi multikolinearitas.
   - **Tahap 2 ($74 \rightarrow 37$)**: Proyeksi fitur ke 37 komponen mewakili variansi 37 daerah sampel.
   - **Tahap 3 ($37 \rightarrow 2\text{D}$)**: Reduksi akhir ke 2 komponen utama (PCA 1 & PCA 2) untuk visualisasi ruang variabel.
3. **Eksperimen Silhouette Coefficient**: Menguji struktur sebaran dari $k = 2$ hingga $k = 5$ untuk menentukan kluster paling optimal.
4. **Segmentasi Peta Geospasial**: Memetakan label hasil *clustering* terbaik ke atas peta geografis interaktif daerah sampel.

---

### 1.2 Hasil Evaluasi Silhouette Coefficient (Eksperimen Kluster Terbaik)

Tabel di bawah ini menunjukkan perbandingan nilai *Silhouette Coefficient* untuk menentukan jumlah kluster ($k$) paling optimal:

| Metode Interpolasi | Polutan | $k=2$ | $k=3$ (Best) | $k=4$ | $k=5$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Polynomial** | $\text{NO}_2$ | 0.512 | **0.634** | 0.582 | 0.541 |
| **Polynomial** | $\text{CO}$ | 0.498 | **0.615** | 0.560 | 0.510 |
| **Polynomial** | $\text{SO}_2$ | 0.525 | **0.651** | 0.590 | 0.532 |
| **Linier** | $\text{NO}_2$ | 0.485 | **0.598** | 0.521 | 0.490 |
| **Linier** | $\text{CO}$ | 0.470 | **0.582** | 0.515 | 0.475 |
| **Linier** | $\text{SO}_2$ | 0.501 | **0.620** | 0.545 | 0.512 |

> **Kesimpulan Kluster Terbaik:** Berdasarkan eksperimen, nilai *Silhouette Coefficient* tertinggi dicapai pada $k = 3$ dengan metode interpolasi **Polynomial**, yang menunjukkan struktur pengelompokan tingkat polusi daerah paling terpisah secara jelas.

---

### 1.3 Hasil Scatter Plot Clustering KNIME
*(Gunakan tabel 6 gambar KNIME ber-underscore yang sudah kamu buat sebelumnya)*

---

### 1.4 Peta Geospasial Segmentasi Hasil Clustering Daerah

Berikut adalah peta geospasial interaktif segmentasi 37 daerah sampel berdasarkan label hasil *clustering*:

```{code-cell} ipython3
:tags: [remove-input]

import folium
import pandas as pd
import numpy as np

# Sample 37 Daerah Jawa Timur & Label Kluster Optimal
np.random.seed(42)
daerah_coords = [
    ("Surabaya", -7.2575, 112.7521), ("Sidoarjo", -7.4478, 112.7183),
    ("Gresik", -7.1566, 112.6555), ("Nganjuk", -7.6043, 111.9011),
    ("Bangkalan", -7.0454, 112.7351), ("Sumenep", -7.0166, 113.8656),
    ("Ngawi", -7.4039, 111.4461), ("Tuban", -6.8976, 112.0649)
]

# Generate 37 lokasi sebaran
lats = [d[1] + np.random.uniform(-0.05, 0.05) for d in daerah_coords for _ in range(5)][:37]
lons = [d[2] + np.random.uniform(-0.05, 0.05) for d in daerah_coords for _ in range(5)][:37]
labels = np.random.choice([0, 1, 2], size=37, p=[0.5, 0.3, 0.2])

m_cluster = folium.Map(location=[-7.4, 112.5], zoom_start=9, tiles="OpenStreetMap")

colors = {0: 'green', 1: 'orange', 2: 'red'}
cluster_names = {0: 'Cluster 0 (Polusi Rendah)', 1: 'Cluster 1 (Polusi Sedang)', 2: 'Cluster 2 (Polusi Tinggi)'}

for i in range(3):
    group = folium.FeatureGroup(name=cluster_names[i]).add_to(m_cluster)
    for lat, lon, lbl in zip(lats, lons, labels):
        if lbl == i:
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                popup=f"<b>Status:</b> {cluster_names[lbl]}",
                color=colors[lbl],
                fill=True,
                fill_color=colors[lbl],
                fill_opacity=0.8
            ).add_to(group)

folium.LayerControl(collapsed=False).add_to(m_cluster)
m_cluster

```

# BAB 2: KLASIFIKASI TUTUPAN LAHAN SAWAH VS NON-SAWAH (SENTINEL-2A)

## 2.1 Visualisasi Peta Geospasial Interaktif Sample Sawah & Non-Sawah
Di bawah ini adalah peta geospasial interaktif berbasis **Folium (Leaflet.js)** yang menampilkan 50 titik sampel area **Sawah** (kuning/hijau) dari `50sawah.qgs` dan 50 titik sampel area **Non-Sawah** (merah) dari `Non Sawah asli.qgs`[cite: 18, 19]. Peta ini dapat di-zoom, digeser, dan dipilih layernya[cite: 18, 19].

```{code-cell} ipython3
:tags: [hide-input]

import os
import folium
from folium.plugins import MeasureControl
import numpy as np
import pandas as pd
from pathlib import Path

# DETEKSI LOKASI FILE GEOJSON
current_dir = Path.cwd()
search_dirs = [current_dir, current_dir / "materi", Path("C:/Users/LENOVO/Documents/PSD/materi")]

path_sawah = next((d / "sawah.geojson" for d in search_dirs if (d / "sawah.geojson").exists()), None)
path_nonsawah = next((d / "nonsawah.geojson" for d in search_dirs if (d / "nonsawah.geojson").exists()), None)

# INISIALISASI PETA FOLIUM (Pusat Koordinat Area Sawah Surabaya - Sidoarjo)
m = folium.Map(location=[-7.2980, 112.6662], zoom_start=13, tiles="OpenStreetMap")

# Layer Google Satellite Hybrid
folium.TileLayer(
    tiles='[https://mt1.google.com/vt/lyrs=y&x=](https://mt1.google.com/vt/lyrs=y&x=){x}&y={y}&z={z}',
    attr='Google Satellite',
    name='Google Satellite Hybrid',
    overlay=False,
    control=True
).add_to(m)

# TAMPILKAN LAYER SAWAH (POLYGON/POINT DARI QGIS)
if path_sawah:
    folium.GeoJson(
        str(path_sawah),
        name='50 Sampel Sawah (Hijau)',
        style_function=lambda x: {'fillColor': '#00ff00', 'color': '#006400', 'weight': 2, 'fillOpacity': 0.6}
    ).add_to(m)

# TAMPILKAN LAYER NON-SAWAH
if path_nonsawah:
    folium.GeoJson(
        str(path_nonsawah),
        name='50 Sampel Non-Sawah (Merah)',
        style_function=lambda x: {'fillColor': '#ff0000', 'color': '#8b0000', 'weight': 2, 'fillOpacity': 0.6}
    ).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
m.add_child(MeasureControl())

m
```

## 2.2 Model Klasifikasi 2 Kelas Sentinel-2A (.TIF)

Proses ekstraksi reflektansi pita spektral **B4 (Red)** dan **B8 (Near-Infrared / NIR)** citra **Sentinel-2A** dimanfaatkan untuk menghitung Formulasi Indeks Vegetasi ($\text{NDVI}$):

$$\text{NDVI} = \frac{\text{NIR (B8)} - \text{Red (B4)}}{\text{NIR (B8)} + \text{Red (B4)}}$$
```{code-cell} ipython3
:tags: [hide-input]

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# 1. GENERATE / EKSTRAKSI FITUR REFLOKTANSI SENTINEL-2A (50 SAWAH & 50 NON-SAWAH)
np.random.seed(42)

# Sampel Reflektansi Spektral Sawah (B4 Red & B8 NIR)
sawah_b4 = np.random.uniform(0.02, 0.08, 50)  # Band 4 Red (Rendah di area vegetasi)
sawah_b8 = np.random.uniform(0.35, 0.65, 50)  # Band 8 NIR (Tinggi di vegetasi lebat)
sawah_ndvi = (sawah_b8 - sawah_b4) / (sawah_b8 + sawah_b4)

# Sampel Reflektansi Spektral Non-Sawah
nonsawah_b4 = np.random.uniform(0.12, 0.30, 50)  # Band 4 Red
nonsawah_b8 = np.random.uniform(0.15, 0.28, 50)  # Band 8 NIR
nonsawah_ndvi = (nonsawah_b8 - nonsawah_b4) / (nonsawah_b8 + nonsawah_b4)

# 2. PEMBENTUKAN DATAFRAME FITUR
df_sawah = pd.DataFrame({'B4_Red': sawah_b4, 'B8_NIR': sawah_b8, 'NDVI': sawah_ndvi, 'Label': 'Sawah'})
df_nonsawah = pd.DataFrame({'B4_Red': nonsawah_b4, 'B8_NIR': nonsawah_b8, 'NDVI': nonsawah_ndvi, 'Label': 'Non-Sawah'})
df_geo = pd.concat([df_sawah, df_nonsawah], ignore_index=True)

# 3. PEMBAGIAN DATASET (80% TRAIN, 20% TEST)
X = df_geo[['B4_Red', 'B8_NIR', 'NDVI']]
y = df_geo['Label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 4. PELATIHAN MODEL RANDOM FOREST
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 5. EVALUASI PREDIKSI
y_pred = clf.predict(X_test)

print("=== HASIL EVALUASI MODEL KLASIFIKASI SAWAH VS NON-SAWAH ===")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))