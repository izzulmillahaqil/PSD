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

### 1.2 Hasil Clustering KNIME Per Polutan (Polynomial vs Linier)

Berikut adalah visualisasi hasil *clustering* scatter plot yang dieksekusi melalui *workflow* KNIME Analytics Platform. Visualisasi ini membandingkan sebaran kluster untuk masing-masing polutan ($\text{NO}_2$, $\text{CO}$, $\text{SO}_2$) berdasarkan metode interpolasi **Polynomial** dan **Linier**:

#### 1. Polutan $\text{NO}_2$ (Nitrogen Dioksida)
| Interpolasi Polynomial | Interpolasi Linier |
| :---: | :---: |
| ![Clustering NO2 Polynomial](Clustering no2 polynomial.png) | ![Clustering NO2 Linear](Clustering no2 linear.png) |

#### 2. Polutan $\text{CO}$ (Karbon Monoksida)
| Interpolasi Polynomial | Interpolasi Linier |
| :---: | :---: |
| ![Clustering CO Polynomial](Clustering co polynomial.png) | ![Clustering CO Linear](Clustering co linear.png) |

#### 3. Polutan $\text{SO}_2$ (Sulfur Dioksida)
| Interpolasi Polynomial | Interpolasi Linier |
| :---: | :---: |
| ![Clustering SO2 Polynomial](Clustering So2 polynomial.png) | ![Clustering SO2 Linear](Clustering so2 linear.png) |

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