# 6. Ekstraksi Fitur TSFEL
Dokumen ini menjelaskan alur pra-pemrosesan data polutan $NO_2$ wilayah **Surabaya Selatan** serta ekstraksi **68 fitur time-series** menggunakan pustaka **TSFEL** (*Time Series Feature Extraction Library*).

---

## 1. Pra-pemrosesan Data (Deteksi Outlier & Imputasi)

1. **Deteksi Pencilan (*Outlier Detection*)**:
   Menggunakan metode *Interquartile Range* (IQR):
   $$\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}$$
   $$\text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$$
   Nilai pencilan di luar rentang ini dikonversi menjadi `NaN`.

2. **Imputasi Nilai Kosong (*Missing Value Imputation*)**:
   Seluruh nilai `NaN` diimputasi berbasis deret waktu (*linear time interpolation*) dilanjutkan *Forward Fill* (`ffill`) dan *Backward Fill* (`bfill`) hingga $0 \text{ missing value}$.

---

## 2. Rincian 68 Fitur TSFEL Berdasarkan Domain

Ekstraksi fitur dilakukan pada sinyal 1D $NO_2$ terimputasi untuk menghasilkan **68 fitur unik** yang terbagi menjadi 3 domain utama:

### A. Domain Statistik (Statistical Domain)
Domain ini menggambarkan distribusi, pemusatan data, serta energi gelombang sinyal $NO_2$:

| Nama Fitur | Nilai |
| :--- | :--- |
| `abs_energy` | `6.1646e-07` |
| `auc` | `0.01436` |
| `calc_max` | `7.3105e-05` |
| `calc_mean` | `3.9620e-05` |
| `calc_median` | `4.0933e-05` |
| `calc_min` | `6.2984e-06` |
| `calc_std` | `1.1335e-05` |
| `calc_var` | `1.2848e-10` |
| `entropy` | `1.0` |
| `hist_mode` | `4.3042e-05` |
| `interq_range` | `1.5633e-05` |
| `kurtosis` | `0.11496` |
| `maximum_fractal_length` | `-2.5804` |
| `mean_abs_deviation` | `9.0568e-06` |
| `median_abs_deviation` | `7.6239e-06` |
| `mse` | `0.73851` |
| `pk_pk_distance` | `6.6806e-05` |
| `rms` | `4.1210e-05` |
| `skewness` | `-0.18384` |
| `sum_abs_diff` | `0.00219` |
| `wavelet_abs_mean` | `1.9056e-06` |
| `wavelet_energy` | `1.8054e-05` |
| `wavelet_entropy` | `2.1324` |
| `wavelet_std` | `1.7932e-05` |
| `wavelet_var` | `3.4725e-10` |

---

### B. Domain Temporal (Temporal Domain)
Domain ini mengukur dinamika waktu lokal, transisi nilai, dan fluktuasi antar-sampel berurutan:

| Nama Fitur | Nilai |
| :--- | :--- |
| `autocorr` | `3.0` |
| `dfa` | `0.91596` |
| `distance` | `362.0` |
| `ecdf` | `0.01515` |
| `ecdf_percentile` | `3.9713e-05` |
| `ecdf_percentile_count` | `181.0` |
| `ecdf_slope` | `38197.50906` |
| `higuchi_fractal_dimension` | `1.8248` |
| `human_range_energy` | `0.0` |
| `hurst_exponent` | `0.84544` |
| `lempel_ziv` | `0.17080` |
| `mean_abs_diff` | `6.0430e-06` |
| `mean_diff` | `-2.7141e-08` |
| `median_abs_diff` | `2.7729e-06` |
| `median_diff` | `-3.1096e-07` |
| `negative_turning` | `56.0` |
| `neighbourhood_peaks` | `13.0` |
| `petrosian_fractal_dimension` | `1.0201` |
| `positive_turning` | `56.0` |
| `slope` | `-8.7264e-09` |
| `zero_cross` | `0.0` |

---

### C. Domain Spektral & Lainnya (Spectral Domain & Coefficients)
Domain ini menganalisis komposisi frekuensi spektrum daya serta koefisien tambahan:

| Nama Fitur | Nilai |
| :--- | :--- |
| `average_power` | `1.7029e-09` |
| `calc_centroid` | `176.86884` |
| `fundamental_frequency` | `0.00275` |
| `lpcc` | `0.76505` |
| `max_frequency` | `0.43526` |
| `max_power_spectrum` | `22.77502` |
| `median_frequency` | `0.05785` |
| `mfcc` | `21.05104` |
| `power_bandwidth` | `0.36915` |
| `spectral_centroid` | `0.12358` |
| `spectral_decrease` | `-2.66955` |
| `spectral_distance` | `-2.05912` |
| `spectral_entropy` | `0.81148` |
| `spectral_kurtosis` | `2.72284` |
| `spectral_positive_turning` | `58.0` |
| `spectral_roll_off` | `0.43526` |
| `spectral_roll_on` | `1.00971` |
| `spectral_skewness` | `-0.03298` |
| `spectral_slope` | `0.14739` |
| `spectral_spread` | `0.58044` |
| `spectral_variation` | `2.2919e-10` |
| `spectrogram_mean_coeff` | `0.00219` |



---

## 4. Kode Deteksi Outlier & Imputasi

Skrip berikut digunakan untuk mendeteksi *outlier*, menggantinya menjadi `NaN`, melakukan interpolasi linier, serta memvisualisasikan perbandingannya:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data CSV
df = pd.read_excel('.../data_polutan_no2_clean.csv') # atau read_csv sesuai formatmu
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# Filter rentang tanggal
df = df[(df["date"] >= "2025-08-31") & (df["date"] <= "2026-08-31")].reset_index(drop=True)

# Deteksi Outlier IQR
Q1 = df["NO2"].quantile(0.25)
Q3 = df["NO2"].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers_mask = (df["NO2"] < lower_bound) | (df["NO2"] > upper_bound)

# Imputasi NaN
df_fixed = df.copy()
df_fixed.loc[outliers_mask, "NO2"] = np.nan
df_fixed["NO2"] = df_fixed["NO2"].interpolate(method="time").ffill().bfill()