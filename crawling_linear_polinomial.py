import numpy as np
import pandas as pd

# 1. Membaca Dataset
# Membaca file dan menjadikan kolom 'date' sebagai index yang bertipe datetime
# Hal ini penting agar proses interpolasi data waktu menjadi lebih akurat
df = pd.read_csv(
    'Semua_Polutan_204_Fitur_TSFEL.csv', parse_dates=['date'], index_col='date'
)

print('Jumlah Missing Value Asli:\n', df.isnull().sum())


# 2. Fungsi untuk mendeteksi Outlier dan mengubahnya menjadi NaN
def hapus_outlier_iqr(series):
  Q1 = series.quantile(0.25)
  Q3 = series.quantile(0.75)
  IQR = Q3 - Q1
  batas_bawah = Q1 - 1.5 * IQR
  batas_atas = Q3 + 1.5 * IQR

  # Ubah nilai di luar batas IQR menjadi NaN (Missing Value)
  return series.mask((series < batas_bawah) | (series > batas_atas))


# Terapkan fungsi ke semua kolom polutan (CO, NO2, SO2)
df_bersih = df.copy()
for kolom in ['CO', 'NO2', 'SO2']:
  df_bersih[kolom] = hapus_outlier_iqr(df[kolom])

print(
    '\nJumlah Missing Value setelah Outlier diubah jadi NaN:\n',
    df_bersih.isnull().sum(),
)

# 3. INTERPOLASI MISSING VALUES

# --- Metode A: Interpolasi Linear ---
# Mengisi kekosongan dengan menarik garis lurus (linear regresi antar dua titik terdekat)
df_linear = df_bersih.interpolate(method='linear')

# Jika ada NaN di baris paling pertama atau terakhir yang tidak terjangkau interpolasi,
# kita gunakan backfill (bfill) dan forwardfill (ffill) untuk meratakannya.
df_linear = df_linear.bfill().ffill()


# --- Metode B: Interpolasi Polinomial (Orde 2) ---
# Menggunakan persamaan kuadratik untuk membentuk kurva yang lebih halus dalam mengisi data
df_poly = df_bersih.interpolate(method='polynomial', order=2)

# Tangani sisa NaN di ujung data (bawaan dari sifat interpolasi polinomial)
df_poly = df_poly.bfill().ffill()


# 4. Tampilkan Hasil
print('\n--- Cek Missing Value Setelah Interpolasi Linear ---')
print(df_linear.isnull().sum())  # Seharusnya semuanya 0

print('\n--- Cek Missing Value Setelah Interpolasi Polynomial ---')
print(df_poly.isnull().sum())  # Seharusnya semuanya 0

print('\nCuplikan Data Hasil Interpolasi Linear:')
print(df_linear.head())

print('\nCuplikan Data Hasil Interpolasi Polynomial:')
print(df_poly.head())

df_linear.to_csv('Polutan_Surabaya_Selatan_Linear.csv')
df_poly.to_csv('Polutan_Surabaya_Selatan_Poly.csv')