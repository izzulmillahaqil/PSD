# 4. Analisis Time Series

Tahap ini menyajikan visualisasi tren konsentrasi $NO_2$ harian untuk melihat dinamika kualitas udara selama rentang waktu pengamatan.

## Visualisasi Fluktuasi NO2

Grafik di bawah ini menampilkan tingkat konsentrasi $NO_2$ ($\text{mol/m}^2$) dari 1 September 2025 hingga 31 Agustus 2026.

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset clean
df = pd.read_csv('../data/processed/data_polutan_no2_clean.csv')
df['date'] = pd.to_datetime(df['date'])

# Plotting grafik time-series
plt.figure(figsize=(10, 4))
plt.plot(df['date'], df['NO2_clean'], color='#1f77b4', marker='o', linewidth=2, label='NO2 Concentration')

plt.title('Tren Konsentrasi NO2 Troposferik (2025 - 2026)', fontsize=12, fontweight='bold')
plt.xlabel('Tanggal', fontsize=10)
plt.ylabel('Konsentrasi NO2 (mol/m²)', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()
```

## Evaluasi Tren & Pola

* **Variasi Musiman**: Nilai konsentrasi cenderung menurun pada puncak musim hujan karena efek *wet deposition* (peluruhan polutan oleh air hujan).
* **Puncak Emisi**: Fluktuasi tinggi berulang pada periode aktivitas transportasi dan industri harian.