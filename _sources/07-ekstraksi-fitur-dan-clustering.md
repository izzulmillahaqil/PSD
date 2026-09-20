---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
---

# 7. Ekstraksi Fitur TSFEL, Reduksi PCA, & K-Means Clustering

Dokumen ini menjelaskan alur lengkap pengolahan data polutan udara (**CO, $NO_2$, dan $SO_2$**) wilayah **Surabaya Selatan** (rentang waktu 31 Agustus 2025 s.d. 31 Agustus 2026), mulai dari eksplorasi deret waktu, ekstraksi 68 fitur TSFEL per polutan (total 204 kolom), reduksi dimensi menggunakan PCA, hingga analisis *K-Means Clustering* dan integrasi database Aiven Cloud.

---

## 1. Eksplorasi Data & Time Series Plot (Semua Polutan)

Sebelum melakukan ekstraksi fitur, kita melakukan visualisasi deret waktu (*time series plot*) untuk melihat tren harian dan karakteristik fluktuasi dari ketiga polutan secara bersamaan.

```{code-cell} ipython3
:tags: [hide-input]

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

pollutants = ['CO', 'NO2', 'SO2']
CONTAMINATION = 0.05

for pol in pollutants:
    try:
        # 1. Load data
        df = pd.read_csv(f"data/processed/data_polutan_{pol.lower()}_clean.csv")
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # Parse data numerik
        def parse_val(v):
            if pd.isna(v) or v is None: return np.nan
            s = str(v).replace('[', '').replace(']', '').strip()
            return float(s) if s.lower() not in ['none', 'nan', ''] else np.nan

        df[pol] = df[pol].apply(parse_val)
        df = df.dropna(subset=[pol]).copy()

        # 2. Deteksi Outlier dengan Isolation Forest
        model = IsolationForest(contamination=CONTAMINATION, random_state=42)
        df['anomaly'] = model.fit_predict(df[[pol]])  # -1 = outlier, 1 = normal
        outliers = df[df['anomaly'] == -1]

        # 3. Ganti Outlier jadi NaN lalu Interpolasi Berbasis Waktu
        df_fixed = df.copy()
        df_fixed.loc[df_fixed['anomaly'] == -1, pol] = np.nan
        df_fixed[pol] = df_fixed[pol].interpolate(method='linear').ffill().bfill()

        # 4. Visualisasi Plot Sebelum vs Sesudah (Persis Gambar)
        fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True)

        # Plot Sebelum Perbaikan
        axes[0].plot(df['date'], df[pol], label=f'{pol} (asli)', linewidth=1)
        axes[0].scatter(outliers['date'], outliers[pol], color='red', 
                        marker='o', label='Outlier (Isolation Forest)', zorder=5)
        axes[0].set_title(f'Sebelum Perbaikan - Deteksi Outlier {pol}')
        axes[0].legend(loc='upper right')

        # Plot Sesudah Perbaikan
        axes[1].plot(df_fixed['date'], df_fixed[pol], color='green', linewidth=1, 
                     label=f'{pol} (setelah outlier diganti & diinterpolasi)')
        axes[1].set_title(f'Sesudah Perbaikan Outlier {pol}')
        axes[1].legend(loc='upper right')

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Gagal memproses visualisasi polutan {pol}: {e}")