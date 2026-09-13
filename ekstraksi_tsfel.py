import pandas as pd
import numpy as np
import inspect
import ast
import tsfel.feature_extraction.features as tsfel_features

# ---------- 1. Muat dan bersihkan data ----------
df = pd.read_csv('data/processed/data_polutan_no2_clean.csv')

# Jika ada kolom date, urutkan berdasarkan tanggal
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

target_pollutant = 'NO2'

# --- PERBAIKAN UTAMA: PARSER UNTUK MEMBACA STRING KURUNG SIKU '[0.000035]' JADI FLOAT ---
def parse_val(val):
    if pd.isna(val) or str(val).strip() in ['None', '[None]', '', 'nan']:
        return np.nan
    s = str(val).strip()
    try:
        if s.startswith('[') and s.endswith(']'):
            parsed = ast.literal_eval(s)
            if isinstance(parsed, list) and len(parsed) > 0:
                return float(parsed[0])
        return float(s.replace('[', '').replace(']', ''))
    except:
        return np.nan

# Terapkan parser angka ke kolom NO2
df[target_pollutant] = df[target_pollutant].apply(parse_val)

n_missing_before = df[target_pollutant].isna().sum()
print(f"Jumlah NaN/missing sebelum pembersihan: {n_missing_before}")

# Deteksi Outlier dengan IQR & ubah outlier jadi NaN
Q1 = df[target_pollutant].quantile(0.25)
Q3 = df[target_pollutant].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df.loc[(df[target_pollutant] < lower_bound) | (df[target_pollutant] > upper_bound), target_pollutant] = np.nan

# Imputasi Missing Value & Outliers (Interpolasi Linear + ffill + bfill)
if 'date' in df.columns:
    df_clean = df.set_index('date').interpolate(method='time').ffill().bfill()
else:
    df_clean = df.interpolate(method='linear').ffill().bfill()

# Pastikan data terisi penuh (0 NaN)
signal_1d = df_clean[target_pollutant].astype(float).values
print(f"Total sampel data NO2 siap diekstraksi: {len(signal_1d)} baris")
print(f"Sisa NaN setelah imputasi: {np.isnan(signal_1d).sum()}")

fs = 1

# ---------- 2. Daftar PERSIS 68 fitur TSFEL ----------
FEATURE_LIST = """abs_energy auc autocorr average_power calc_centroid calc_max calc_mean
calc_median calc_min calc_std calc_var dfa distance ecdf ecdf_percentile ecdf_percentile_count
ecdf_slope entropy fundamental_frequency higuchi_fractal_dimension hist_mode human_range_energy
hurst_exponent interq_range kurtosis lempel_ziv lpcc max_frequency max_power_spectrum
maximum_fractal_length mean_abs_deviation mean_abs_diff mean_diff median_abs_deviation
median_abs_diff median_diff median_frequency mfcc mse negative_turning neighbourhood_peaks
petrosian_fractal_dimension pk_pk_distance positive_turning power_bandwidth rms skewness slope
spectral_centroid spectral_decrease spectral_distance spectral_entropy spectral_kurtosis
spectral_positive_turning spectral_roll_off spectral_roll_on spectral_skewness spectral_slope
spectral_spread spectral_variation spectrogram_mean_coeff sum_abs_diff wavelet_abs_mean
wavelet_energy wavelet_entropy wavelet_std wavelet_var zero_cross""".split()


def to_scalar(result):
    if isinstance(result, dict) and "values" in result:
        result = result["values"]
    if isinstance(result, (list, tuple, np.ndarray)):
        arr = np.asarray(result, dtype=float)
        return float(np.nanmean(arr))
    return float(result)


def extract_one(fn_name, signal, fs):
    fn = getattr(tsfel_features, fn_name)
    params = inspect.signature(fn).parameters
    if "fs" in params:
        result = fn(signal, fs)
    else:
        result = fn(signal)
    return to_scalar(result)


row = {}
for fn_name in FEATURE_LIST:
    try:
        row[fn_name] = extract_one(fn_name, signal_1d, fs)
    except Exception as e:
        row[fn_name] = np.nan

extracted_features_final = pd.DataFrame([row])

output_name = 'data/processed/NO2_Surabaya_Selatan_TSFEL.csv'
extracted_features_final.to_csv(output_name, index=False)

print(f"\nBerhasil! Jumlah fitur yang dihasilkan: {extracted_features_final.shape[1]}")
print(f"File tersimpan di: {output_name}")