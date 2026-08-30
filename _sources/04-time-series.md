# 4. Analisis Time Series

Tahap ini menampilkan visualisasi tren konsentrasi polutan dari waktu ke waktu untuk memahami pola perubahan kualitas udara di wilayah pengamatan.

## Grafik Tren Konsentrasi NO2 (1 Thn Terakhir)

Berikut adalah grafik pola fluktuasi polutan $NO_2$ periode 1 September 2025 – 31 Agustus 2026:

{code-cell} ipython3
import pandas as pd
import matplotlib.pyplot as plt

# Load data polutan yang sudah dibersihkan
# Sesuaikan path jika file csv kamu berada di lokasi lain
df = pd.read_csv('data/processed/data_polutan_no2_clean.csv')
df['Date'] = pd.to_datetime(df['Date'])

plt.figure(figsize=(12, 5))
plt.plot(df['Date'], df['NO2_concentration'], color='#d9534f', linewidth=1.5, label='NO2 Concentration')
plt.title('Pola Konsentrasi Polutan NO2 (Sep 2025 - Ags 2026)', fontsize=14, fontweight='bold')
plt.xlabel('Tanggal', fontsize=12)
plt.ylabel('Konsentrasi (mol/m²)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()