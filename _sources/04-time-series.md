# 4. Analisis Time Series

Tahap ini menyajikan visualisasi tren konsentrasi $NO_2$ harian dan *rolling average* (rata-rata bergerak) untuk melihat dinamika kualitas udara selama rentang waktu pengamatan.

## Visualisasi Fluktuasi NO2

Grafik di bawah ini menampilkan tingkat konsentrasi $NO_2$ ($\text{mol/m}^2$) dari 1 September 2025 hingga 31 Agustus 2026.

```{code-cell} ipython3
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset clean
df = pd.read_csv('data/processed/data_polutan_no2_clean.csv')
df['date'] = pd.to_datetime(df['date'])

# Hitung 7-day rolling average untuk memperhalus tren
df['NO2_7day'] = df['NO2_clean'].rolling(window=7).mean()

# Plotting grafik time-series
plt.figure(figsize=(14, 6))
plt.plot(df['date'], df['NO2_clean'], alpha=0.4, color='gray', label='Harian (Raw)')
plt.plot(df['date'], df['NO2_7day'], color='#1f77b4', linewidth=2, label='Rata-rata 7 Harian')

plt.title('Tren Konsentrasi NO2 Troposferik Sentinel-5P (2025 - 2026)', fontsize=14, fontweight='bold')
plt.xlabel('Tanggal', fontsize=11)
plt.ylabel('Konsentrasi NO2 (mol/m²)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()