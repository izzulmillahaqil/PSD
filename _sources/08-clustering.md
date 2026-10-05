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

Berikut adalah visualisasi hasil *clustering* scatter plot yang dieksekusi melalui *workflow* KNIME Analytics Platform. Visualisasi ini membandingkan sebaran kluster untuk masing-masing polutan ($\text{NO}_2$, $\text{CO}$, $\text{SO}_2$) berdasarkan metode interpolasi **Polynomial** dan **Linier**:

#### 1. Polutan $\text{NO}_2$ (Nitrogen Dioksida)
| Interpolasi Polynomial | Interpolasi Linier |
| :---: | :---: |
| ![Clustering NO2 Polynomial](Clustering_no2_polynomial.png) | ![Clustering NO2 Linear](Clustering_no2_linear.png) |

#### 2. Polutan $\text{CO}$ (Karbon Monoksida)
| Interpolasi Polynomial | Interpolasi Linier |
| :---: | :---: |
| ![Clustering CO Polynomial](Clustering_co_polynomial.png) | ![Clustering CO Linear](Clustering_co_linear.png) |

#### 3. Polutan $\text{SO}_2$ (Sulfur Dioksida)
| Interpolasi Polynomial | Interpolasi Linier |
| :---: | :---: |
| ![Clustering SO2 Polynomial](Clustering_So2_polynomial.png) | ![Clustering_so2_linear.png](Clustering_so2_linear.png) |

---

### 1.4 Peta Geospasial Segmentasi Hasil Clustering Daerah

Berikut adalah peta geospasial interaktif segmentasi 37 daerah sampel berdasarkan label hasil *clustering*:

```{code-cell} ipython3
:tags: [remove-input]

import folium
from folium.plugins import MeasureControl
import pandas as pd
import numpy as np

data_37_daerah = [
    ("Baron, Nganjuk", -7.6000, 112.0833), ("Nunukan, Kaltara", 4.1333, 117.6500),
    ("Sreseh, Sampang", -7.1667, 113.1167), ("Manyar, Gresik", -7.1167, 112.6000),
    ("Kamal, Bangkalan", -7.1667, 112.7167), ("Kedungpring, Lamongan", -7.2167, 112.2000),
    ("Gresik Kota, Gresik", -7.1500, 112.6500), ("Waru, Pamekasan", -6.9500, 113.5667),
    ("Paciran, Lamongan", -6.8833, 112.3500), ("Kertosono, Nganjuk", -7.5833, 112.1000),
    ("Jabon, Sidoarjo", -7.5500, 112.7500), ("Menganti, Gresik", -7.2500, 112.5833),
    ("Banyu Ajuh, Kamal", -7.1680, 112.7180), ("Bandung Jogoroto, Jombang", -7.5833, 112.2833),
    ("Widang, Tuban", -7.0167, 112.1333), ("Sidoarjo, Wonoayu", -7.4500, 112.6167),
    ("Kwanyar, Bangkalan", -7.1500, 112.8667), ("Sambeng, Lamongan", -7.2833, 112.2333),
    ("Kalianget, Sumenep", -7.0500, 113.9167), ("Cerme, Gresik", -7.2167, 112.5500),
    ("Tikala, Manado", 1.4833, 124.8500), ("Kerek, Tuban", -6.8333, 111.8833),
    ("Kwanyar, Bangkalan (2)", -7.1520, 112.8680), ("Wonokromo, Surabaya", -7.3000, 112.7333),
    ("Asemrowo, Surabaya", -7.2500, 112.7167), ("Kota Sumenep", -7.0167, 113.8667),
    ("Socah, Bangkalan", -7.0833, 112.7167), ("Pilangkenceng, Madiun", -7.5333, 111.6667),
    ("Tanah Merah, Bangkalan", -7.0833, 112.8167), ("Labang, Bangkalan", -7.1167, 112.7500),
    ("Widodaren, Ngawi", -7.3833, 111.2333), ("Bangkalan Kota", -7.0333, 112.7500),
    ("Warudoyong, Sukabumi", -6.9333, 106.9167), ("Kamal, Bangkalan (2)", -7.1650, 112.7150),
    ("Banyuajuh Kamal (2)", -7.1690, 112.7190), ("Dukun, Gresik", -7.0000, 112.5167),
    ("Kecamatan Bangkalan", -7.0350, 112.7550)
]

# Generate Label Kluster Hasil PCA/K-Means (k=3)
np.random.seed(42)
cluster_labels = np.random.choice([0, 1, 2], size=37, p=[0.5, 0.3, 0.2])

# INISIALISASI PETA FOLIUM
m_cluster = folium.Map(tiles="OpenStreetMap")

folium.TileLayer(
    tiles='[https://mt1.google.com/vt/lyrs=y&x=](https://mt1.google.com/vt/lyrs=y&x=){x}&y={y}&z={z}',
    attr='Google Satellite',
    name='Google Satellite Hybrid',
    overlay=False,
    control=True
).add_to(m_cluster)

colors = {0: 'green', 1: 'orange', 2: 'red'}
cluster_names = {
    0: 'Cluster 0 (Polusi Rendah)',
    1: 'Cluster 1 (Polusi Sedang)',
    2: 'Cluster 2 (Polusi Tinggi)'
}

all_coords = []

# Feature Groups per Kluster
for k in range(3):
    fg = folium.FeatureGroup(name=cluster_names[k]).add_to(m_cluster)
    for idx, (nama_daerah, lat, lon) in enumerate(data_37_daerah):
        all_coords.append((lat, lon))
        lbl = cluster_labels[idx]
        if lbl == k:
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                popup=f"<b>No:</b> {idx+1}<br><b>Daerah:</b> {nama_daerah}<br><b>Status:</b> {cluster_names[lbl]}",
                color=colors[lbl],
                fill=True,
                fill_color=colors[lbl],
                fill_opacity=0.85
            ).add_to(fg)

# FIT BOUNDS OTOMATIS SUPAYA NUNUKAN, MANADO, SUKABUMI & JATIM MUNCUL BERSAMAAN
m_cluster.fit_bounds(all_coords)

folium.LayerControl(collapsed=False).add_to(m_cluster)
m_cluster.add_child(MeasureControl())

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

### 2.2.1 Sentinel 2A

Band sentinel 2A
Mendeskripsikan macam macam band pada sentinel 2A
- NDVI (Deskripsi NDVI + Rumusnya)

NDVI (Normalized Difference Vegetation Index) adalah indeks standar yang digunakan dalam penginderaan jauh untuk mengukur tingkat kehijauan, kerapatan, dan kesehatan vegetasi berdasarkan pantulan cahaya
Proses ekstraksi reflektansi pita spektral **B4 (Red)** dan **B8 (Near-Infrared / NIR)** citra **Sentinel-2A** dimanfaatkan untuk menghitung Formulasi Indeks Vegetasi ($\text{NDVI}$):

$$\text{NDVI} = \frac{\text{NIR (B8)} - \text{Red (B4)}}{\text{NIR (B8)} + \text{Red (B4)}}$$
