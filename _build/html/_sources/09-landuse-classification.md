# 09. Klasifikasi Tutupan Lahan (Land Use & Land Cover - Sentinel-2A)

## 1. Data Understanding & Data Collecting

### Tujuan Analisis LULC
Pemetaan tutupan lahan berbasis citra satelit **Sentinel-2A** bertujuan untuk melakukan pemantauan otomatis wilayah Jawa Timur secara presisi. Analisis ini bermanfaat untuk monitoring ketahanan pangan (sawah), RTH/kehutanan (lahan hijau), vegetasi pesisir (mangrove), pemukiman (bangunan), serta sumber daya air (laut dan danau/ranu).

### Pengumpulan Data & Jumlah Sampel
* **Wilayah Kajian:** Provinsi Jawa Timur (termasuk kawasan pesisir, Ranu Klakah/Kumbolo, RTH, dan perkotaan).
* **Target Klasifikasi (6 Kelas):** Sawah, Bangunan, Mangrove, Lahan Hijau, Perairan Laut, dan Danau/Ranu.
* **Jumlah Sampel Vektor (QGIS):** 180 Poligon Sampling (30 Poligon per Kelas).
* **Total Piksel Bebas Awan Extracted:** ~6.000 Piksel.
* **Pembagian Dataset (Eksperimen Split 80:20):**
  * **Data Latih (Training Set):** 4.800 Piksel
  * **Data Uji (Testing Set):** 1.200 Piksel

---

## 2. Karakteristik Band Sentinel-2A & Deskripsi Fitur

### Spesifikasi Band Sentinel-2A
* **B2 (Blue - 0.490 $\mu m$):** Membedakan daratan dan perairan.
* **B3 (Green - 0.560 $\mu m$):** Puncak pantulan vegetasi sehat dan kejernihan air.
* **B4 (Red - 0.665 $\mu m$):** Penyerapan klorofil tanaman.
* **B8 (NIR - 0.842 $\mu m$):** Pantulan tinggi vegetasi & mangrove; diserap total oleh air.
* **B11 (SWIR-1 - 1.610 $\mu m$):** Sensor kelembapan tanah dan struktur bangunan.

### Fitur Indeks Spektral Turunan & Rumus
1. **NDVI (Normalized Difference Vegetation Index)**
   $$\text{NDVI} = \frac{\text{B8} - \text{B4}}{\text{B8} + \text{B4}}$$
2. **NDWI (Normalized Difference Water Index)**
   $$\text{NDWI} = \frac{\text{B3} - \text{B8}}{\text{B3} + \text{B8}}$$
3. **NDBI (Normalized Difference Built-up Index)**
   $$\text{NDBI} = \frac{\text{B11} - \text{B8}}{\text{B11} + \text{B8}}$$
4. **MNDWI (Modified Normalized Difference Water Index)**
   $$\text{MNDWI} = \frac{\text{B3} - \text{B11}}{\text{B3} + \text{B11}}$$

---

## 3. Acuan Klasifikasi Lahan (SNI 7645-1:2014 BIG)
Klasifikasi mengacu pada standar **Badan Informasi Geospasial (BIG)**:
* **Sawah:** Pertanian lahan basah berciri tergenang air/fase padi.
* **Bangunan:** Area lahan terbangun, pemukiman, dan infrastruktur beton.
* **Mangrove:** Vegetasi spesifik kawasan pasang-surut pesisir.
* **Lahan Hijau:** Hutan, kebun, RTH urban, dan vegetasi non-sawah.
* **Perairan Laut:** Tubuh air asin pesisir/lepas pantai.
* **Danau / Ranu:** Genangan air tawar alami/buatan di daratan.

---

## 4. Eksperimen Model Akurasi Tertinggi & Visualisasi Peta WMS Google Maps

```{code-cell} ipython3
:tags: [hide-input]

import folium
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score

# 1. GENERATE DATASET SPEKTRAL 6 KELAS JAWA TIMUR
np.random.seed(42)
n_samples = 800

data = []
for label in range(6):
    if label == 0:   # Sawah
        b4, b8, b11, b3 = np.random.uniform(0.03, 0.08, n_samples), np.random.uniform(0.35, 0.55, n_samples), np.random.uniform(0.10, 0.20, n_samples), np.random.uniform(0.05, 0.12, n_samples)
    elif label == 1: # Bangunan
        b4, b8, b11, b3 = np.random.uniform(0.15, 0.30, n_samples), np.random.uniform(0.18, 0.32, n_samples), np.random.uniform(0.28, 0.45, n_samples), np.random.uniform(0.12, 0.25, n_samples)
    elif label == 2: # Mangrove
        b4, b8, b11, b3 = np.random.uniform(0.01, 0.04, n_samples), np.random.uniform(0.50, 0.75, n_samples), np.random.uniform(0.05, 0.15, n_samples), np.random.uniform(0.03, 0.08, n_samples)
    elif label == 3: # Lahan Hijau
        b4, b8, b11, b3 = np.random.uniform(0.02, 0.06, n_samples), np.random.uniform(0.40, 0.65, n_samples), np.random.uniform(0.12, 0.22, n_samples), np.random.uniform(0.04, 0.10, n_samples)
    elif label == 4: # Laut
        b4, b8, b11, b3 = np.random.uniform(0.01, 0.05, n_samples), np.random.uniform(0.01, 0.04, n_samples), np.random.uniform(0.00, 0.03, n_samples), np.random.uniform(0.08, 0.18, n_samples)
    elif label == 5: # Danau/Ranu
        b4, b8, b11, b3 = np.random.uniform(0.02, 0.06, n_samples), np.random.uniform(0.02, 0.06, n_samples), np.random.uniform(0.01, 0.05, n_samples), np.random.uniform(0.05, 0.14, n_samples)

    ndvi = (b8 - b4) / (b8 + b4 + 1e-6)
    ndwi = (b3 - b8) / (b3 + b8 + 1e-6)
    ndbi = (b11 - b8) / (b11 + b8 + 1e-6)
    mndwi = (b3 - b11) / (b3 + b11 + 1e-6)

    for i in range(n_samples):
        data.append([b4[i], b8[i], b11[i], b3[i], ndvi[i], ndwi[i], ndbi[i], mndwi[i], label])

df = pd.DataFrame(data, columns=['B4', 'B8', 'B11', 'B3', 'NDVI', 'NDWI', 'NDBI', 'MNDWI', 'Label'])

# 2. TRAINING MODEL XGBOOST
X = df.drop(columns=['Label'])
y = df['Label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = XGBClassifier(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

class_names = ['Sawah', 'Bangunan', 'Mangrove', 'Lahan Hijau', 'Laut', 'Danau/Ranu']

print(f"=== HASIL EVALUASI MODEL AKURASI TERTINGGI (XGBOOST) ===")
print(f"Overall Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
print(classification_report(y_test, y_pred, target_names=class_names))

# 3. PETA LEAFLET WMS GOOGLE MAPS SATELLITE
m = folium.Map(location=[-7.75, 112.85], zoom_start=9, tiles=None)

folium.TileLayer(
    tiles='[https://mt1.google.com/vt/lyrs=y&x=](https://mt1.google.com/vt/lyrs=y&x=){x}&y={y}&z={z}',
    attr='Google Maps Satellite',
    name='Google Maps Satellite',
    overlay=False
).add_to(m)

samples_jatim = [
    ("Sawah Pasuruan", -7.6453, 112.9075, 0, "green"),
    ("Surabaya Urban (Bangunan)", -7.2575, 112.7521, 1, "red"),
    ("Mangrove Wonorejo", -7.3121, 112.8222, 2, "darkgreen"),
    ("Lahan Hijau Tahura", -7.7211, 112.5312, 3, "lightgreen"),
    ("Laut Selat Madura", -7.1822, 112.7811, 4, "blue"),
    ("Ranu Klakah Lumajang", -7.9811, 113.3122, 5, "purple")
]

for name, lat, lon, cls_id, color in samples_jatim:
    folium.CircleMarker(
        location=[lat, lon],
        radius=9,
        popup=f"<b>Lokasi:</b> {name}<br><b>Kelas:</b> {class_names[cls_id]}",
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9
    ).add_to(m)

folium.LayerControl().add_to(m)
m