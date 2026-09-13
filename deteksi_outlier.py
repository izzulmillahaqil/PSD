import pandas as pd
import numpy as np
import ast

# 1. Load Data Clean
df = pd.read_csv('data/processed/data_polutan_no2_clean.csv')

# --- PERBAIKAN: KONVERSI KOLOM NO2 KE FLOAT ---
def parse_to_float(val):
    if pd.isna(val) or str(val).strip() in ['None', '[None]', '']:
        return np.nan
    try:
        # Jika nilai berbentuk string list seperti '[2.75e-05]'
        parsed = ast.literal_eval(str(val))
        return float(parsed[0]) if isinstance(parsed, list) else float(parsed)
    except:
        try:
            return float(val)
        except:
            return np.nan

# Terapkan konversi ke angka
no2_series = df['NO2'].apply(parse_to_float)

# --- LANGKAH 1: HITUNG BATAS IQR ---
Q1 = no2_series.quantile(0.25)
Q3 = no2_series.quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print(f"Q1 (25%): {Q1}")
print(f"Q3 (75%): {Q3}")
print(f"IQR: {IQR}")
print(f"Batas Bawah (Lower Bound): {lower_bound}")
print(f"Batas Atas (Upper Bound): {upper_bound}")

# --- LANGKAH 2: DETEKSI OUTLIER ---
outliers_mask = (no2_series < lower_bound) | (no2_series > upper_bound)
jumlah_outlier = outliers_mask.sum()
print(f"\nJumlah outlier terdeteksi: {jumlah_outlier} baris")

# --- LANGKAH 3: HILANGKAN OUTLIER (Ubah jadi NaN) ---
no2_series[outliers_mask] = np.nan

# Simpan data yang outlier-nya sudah dihilangkan ke file baru
df['NO2_Clean_Numeric'] = no2_series
df.to_csv('data/processed/data_polutan_no2_no_outlier.csv', index=False)

print("\nSukses! File 'data_polutan_no2_no_outlier.csv' berhasil disimpan.")