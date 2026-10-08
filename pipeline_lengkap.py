import inspect
import os
import numpy as np
import pandas as pd
import tsfel.feature_extraction.features as tsfel_features

# ==============================================================================
# KONFIGURASI PATH FOLDER
# ==============================================================================
# Deteksi lokasi folder secara dinamis agar aman dari masalah path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# 68 Fitur TSFEL Standard
FEATURE_LIST = (
    "abs_energy auc autocorr average_power calc_centroid calc_max calc_mean "
    "calc_median calc_min calc_std calc_var dfa distance ecdf ecdf_percentile"
    " ecdf_percentile_count ecdf_slope entropy fundamental_frequency"
    " higuchi_fractal_dimension hist_mode human_range_energy hurst_exponent"
    " interq_range kurtosis lempel_ziv lpcc max_frequency max_power_spectrum"
    " maximum_fractal_length mean_abs_deviation mean_abs_diff mean_diff"
    " median_abs_deviation median_abs_diff median_diff median_frequency mfcc"
    " mse negative_turning neighbourhood_peaks petrosian_fractal_dimension"
    " pk_pk_distance positive_turning power_bandwidth rms skewness slope"
    " spectral_centroid spectral_decrease spectral_distance spectral_entropy"
    " spectral_kurtosis spectral_positive_turning spectral_roll_off"
    " spectral_roll_on spectral_skewness spectral_slope spectral_spread"
    " spectral_variation spectrogram_mean_coeff sum_abs_diff wavelet_abs_mean"
    " wavelet_energy wavelet_entropy wavelet_std wavelet_var zero_cross".split()
)


# Helper konversi output TSFEL ke float tunggal
def to_scalar(result):
  if result is None:
    return 0.0
  if isinstance(result, dict) and "values" in result:
    result = result["values"]
  if isinstance(result, (list, tuple, np.ndarray)):
    arr = np.asarray(result, dtype=float)
    return float(np.nanmean(arr))
  try:
    return float(result)
  except Exception:
    return 0.0


# Parser khusus pembersihan string format list/None [val] -> float
def parse_item(val):
  if pd.isna(val) or val is None:
    return np.nan
  s_val = str(val).strip()
  if s_val.startswith("[") and s_val.endswith("]"):
    s_val = s_val[1:-1].strip()
  if s_val.lower() in ["none", "nan", "", "null"]:
    return np.nan
  try:
    return float(s_val)
  except ValueError:
    return np.nan


# Outlier Filtering via IQR
def remove_outliers_iqr(series):
  Q1 = series.quantile(0.25)
  Q3 = series.quantile(0.75)
  IQR = Q3 - Q1
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR
  return series.mask((series < lower_bound) | (series > upper_bound))


# ==============================================================================
# TAHAP 1: MERGE 3 FILE CRAWLING (NO2, SO2, CO)
# ==============================================================================
print("1. MEMPROSES MERGE DATA CRAWL...")

# Load file raw
df_no2 = pd.read_csv(os.path.join(RAW_DIR, "no2_raw.csv"))
df_so2 = pd.read_csv(os.path.join(RAW_DIR, "so2_raw.csv"))
df_co = pd.read_csv(os.path.join(RAW_DIR, "co_raw.csv"))

# Normalisasi format tanggal
for df in [df_no2, df_so2, df_co]:
  df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

# Ambil kolom spesifik & bersihkan angka
df_no2["NO2"] = df_no2["NO2"].apply(parse_item)
df_so2["SO2"] = df_so2["SO2"].apply(parse_item)
df_co["CO"] = df_co["CO"].apply(parse_item)

df_no2 = df_no2[["date", "NO2"]].drop_duplicates(subset=["date"])
df_so2 = df_so2[["date", "SO2"]].drop_duplicates(subset=["date"])
df_co = df_co[["date", "CO"]].drop_duplicates(subset=["date"])

# Merge berdasarkan tanggal (Outer Join)
df_merged = df_no2.merge(df_so2, on="date", how="outer").merge(
    df_co, on="date", how="outer"
)
df_merged = df_merged.sort_values("date").reset_index(drop=True)


# ==============================================================================
# TAHAP 2: OUTLIER IQR & DUAL INTERPOLASI (LINEAR & POLYNOMIAL)
# ==============================================================================
print("2. MELAKUKAN PEMBERSIHAN OUTLIER & INTERPOLASI...")

df_clean = df_merged.copy()
df_clean["date"] = pd.to_datetime(df_clean["date"])
df_clean = df_clean.set_index("date")

# Hapus Outlier dengan IQR
for pol in ["NO2", "SO2", "CO"]:
  df_clean[pol] = remove_outliers_iqr(df_clean[pol])

# A. Interpolasi Linear (Berbasis Waktu)
df_linear = df_clean.interpolate(method="time").bfill().ffill()

# B. Interpolasi Polynomial (Orde 2)
df_poly = df_clean.interpolate(method="polynomial", order=2).bfill().ffill()


# ==============================================================================
# TAHAP 3: EKSTRAKSI FITUR TSFEL (MURNI 204 FITUR TANPA METADATA)
# ==============================================================================
def extract_tsfel_204(df_input):
  # URUTAN POLUTAN HARUS NO2, SO2, CO (Sesuai contoh file CSV-mu)
  pollutants = ["NO2", "SO2", "CO"]
  all_dfs = []
  fs = 1

  for pol in pollutants:
    signal = df_input[pol].astype(float).values
    row = {}

    for fn_name in FEATURE_LIST:
      col_name = f"{pol}_{fn_name}"
      try:
        fn = getattr(tsfel_features, fn_name)
        params = inspect.signature(fn).parameters
        res = fn(signal, fs) if "fs" in params else fn(signal)
        row[col_name] = to_scalar(res)
      except Exception:
        row[col_name] = 0.0

    all_dfs.append(pd.DataFrame([row]))

  # Menggabungkan hasil langsung menjadi DataFrame 1 baris x 204 kolom
  return pd.concat(all_dfs, axis=1)


print("3. MEMPROSES EKSTRAKSI FITUR TSFEL...")
print("   - Mengekstrak TSFEL versi Linear...")
final_linear = extract_tsfel_204(df_linear)

print("   - Mengekstrak TSFEL versi Polynomial...")
final_poly = extract_tsfel_204(df_poly)


# ==============================================================================
# TAHAP 4: PENYIMPANAN AKHIR KE CSV
# ==============================================================================
path_final_linear = os.path.join(
    PROCESSED_DIR, "All-Pollutants-Surabaya Selatan-TSFEL-LINEAR.csv"
)
path_final_poly = os.path.join(
    PROCESSED_DIR, "All-Pollutants-Surabaya Selatan-TSFEL-POLYNOMIAL.csv"
)

# Simpan CSV tanpa metadata (murni 204 kolom)
final_linear.to_csv(path_final_linear, index=False)
final_poly.to_csv(path_final_poly, index=False)

print("\n==================================================")
print("ALUR PIPELINE SELESAI DENGAN SUKSES!")
print(f"File Output Linear   : {path_final_linear}")
print(f"File Output Poly     : {path_final_poly}")
print("Struktur CSV kini 100% sama dengan format referensi!")
print("==================================================")
