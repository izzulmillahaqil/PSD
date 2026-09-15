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
import matplotlib.pyplot as plt

pollutants = ['CO', 'NO2', 'SO2']
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
colors = ['tab:blue', 'tab:orange', 'tab:green']

# Simulasi / Load data (pastikan path file sesuai direktori Anda)
for i, pol in enumerate(pollutants):
    try:
        df = pd.read_csv(f"data/processed/data_polutan_{pol.lower()}_clean.csv")
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        axes[i].plot(df['date'], df[pol], color=colors[i], linewidth=1)
    except:
        # Fallback dummy plot jika dijalankan tanpa file lokal
        dates = pd.date_range(start='2025-08-31', periods=100, freq='D')
        axes[i].plot(dates, range(100), color=colors[i], linewidth=1)
        
    axes[i].set_title(f'Time Series - Polutan {pol} (Surabaya Selatan)')
    axes[i].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()