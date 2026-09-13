# 6. Preprocessing & Ekstraksi 68 Fitur TSFEL

Dokumen ini menjelaskan alur pra-pemrosesan data polutan $NO_2$ wilayah **Surabaya Selatan** serta ekstraksi **68 fitur time-series** menggunakan pustaka **TSFEL** (*Time Series Feature Extraction Library*).

---

## 🛠️ 1. Pra-pemrosesan Data (Deteksi Outlier & Imputasi)

1. **Deteksi Pencilan (*Outlier Detection*)**:
   Menggunakan metode *Interquartile Range* (IQR):
   $$\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}$$
   $$\text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$$
   Nilai pencilan di luar rentang ini dikonversi menjadi `NaN`.

2. **Imputasi Nilai Kosong (*Missing Value Imputation*)**:
   Seluruh nilai `NaN` diimputasi berbasis deret waktu (*linear time interpolation*) dilanjutkan *Forward Fill* (`ffill`) dan *Backward Fill* (`bfill`) hingga $0 \text{ missing value}$.

---

## 🧬 2. Ekstraksi 68 Fitur TSFEL

Ekstraksi fitur dilakukan pada sinyal 1D $NO_2$ terimputasi untuk menghasilkan **68 fitur unik** yang mencakup 3 domain utama:

* **Statistical Domain**: `abs_energy`, `calc_max`, `calc_mean`, `calc_median`, `calc_min`, `calc_std`, `calc_var`, `ecdf`, `kurtosis`, `rms`, `skewness`, dll.
* **Temporal Domain**: `auc`, `autocorr`, `entropy`, `mean_abs_diff`, `zero_cross`, `higuchi_fractal_dimension`, `hurst_exponent`, dll.
* **Spectral Domain**: `average_power`, `calc_centroid`, `fundamental_frequency`, `spectral_centroid`, `spectral_entropy`, `wavelet_energy`, dll.

File dataset hasil ekstraksi disimpan dengan nama `NO2_Surabaya_Selatan_TSFEL.csv` dan telah diunggah ke database agregasi kelas.