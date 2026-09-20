````markdown
---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
---

# 7. Ekstraksi Fitur TSFEL, Reduksi PCA, & K-Means Clustering

Dokumen ini menjelaskan alur lengkap pengolahan data polutan udara (**CO, $NO_2$, dan $SO_2$**) wilayah **Surabaya Selatan** pada rentang waktu **31 Agustus 2025 s.d. 31 Agustus 2026**, mulai dari eksplorasi data, preprocessing, penanganan outlier, imputasi missing value, ekstraksi 68 fitur TSFEL untuk masing-masing polutan, hingga pembentukan matriks 204 fitur yang siap digunakan untuk tahap PCA dan K-Means Clustering.

---

## 1. Import Library & Muat Data

Library yang digunakan meliputi `pandas` dan `numpy` untuk pengolahan data, `matplotlib` untuk visualisasi, `PyWavelets` untuk dekomposisi wavelet, serta `TSFEL` untuk ekstraksi fitur deret waktu.

```{code-cell} ipython3

import os
import inspect
import numpy as np
import pandas as pd
import pywt
import matplotlib.pyplot as plt
import tsfel
import tsfel.feature_extraction.features as tsfel_features

# Load Data Polutan Surabaya Selatan
df_co_raw = pd.read_csv(
    'data/processed/data_polutan_co_clean.csv'
)

df_no2_raw = pd.read_csv(
    'data/processed/data_polutan_no2_clean.csv'
)

df_so2_raw = pd.read_csv(
    'data/processed/data_polutan_so2_clean.csv'
)

print("Data CO  :", df_co_raw.shape)
print("Data NO2 :", df_no2_raw.shape)
print("Data SO2 :", df_so2_raw.shape)
````

---

## 2. Eksplorasi Data & Time Series Plot

Sebelum dilakukan preprocessing dan ekstraksi fitur, data divisualisasikan dalam bentuk *time series plot*. Visualisasi ini digunakan untuk melihat tren, pola perubahan, dan fluktuasi masing-masing polutan terhadap waktu.

```{code-cell} ipython3
:tags: [hide-input]

pollutants = ['CO', 'NO2', 'SO2']

fig, axes = plt.subplots(
    3,
    1,
    figsize=(12, 9),
    sharex=True
)

colors = [
    'tab:blue',
    'tab:orange',
    'tab:green'
]

data_raw = {
    'CO': df_co_raw,
    'NO2': df_no2_raw,
    'SO2': df_so2_raw
}

for i, pol in enumerate(pollutants):

    df_plot = data_raw[pol].copy()

    df_plot['date'] = pd.to_datetime(
        df_plot['date']
    )

    df_plot = df_plot.sort_values(
        'date'
    ).reset_index(drop=True)

    df_plot[pol] = pd.to_numeric(
        df_plot[pol],
        errors='coerce'
    )

    axes[i].plot(
        df_plot['date'],
        df_plot[pol],
        color=colors[i],
        linewidth=1
    )

    axes[i].set_title(
        f'Time Series - Polutan {pol} (Surabaya Selatan)'
    )

    axes[i].set_ylabel(pol)
    axes[i].grid(
        True,
        linestyle='--',
        alpha=0.5
    )

axes[-1].set_xlabel('Tanggal')

plt.tight_layout()
plt.show()
```

---

# 3. Preprocessing Data

Sebelum dilakukan ekstraksi fitur TSFEL, data perlu dibersihkan terlebih dahulu.

Tahapan preprocessing yang dilakukan meliputi:

1. Konversi tanggal menjadi format `datetime`.
2. Pengurutan data berdasarkan tanggal.
3. Parsing nilai polutan.
4. Penanganan missing value.
5. Deteksi outlier menggunakan metode **Interquartile Range (IQR)**.
6. Penggantian outlier menjadi `NaN`.
7. Imputasi kembali menggunakan interpolasi berbasis waktu.

---

## 3.1 Deteksi Outlier Menggunakan IQR

Metode **Interquartile Range (IQR)** digunakan untuk mendeteksi nilai yang berada jauh dari distribusi utama data.

Kuartil pertama dan ketiga didefinisikan sebagai:

$$
Q_1 = \text{Kuartil Pertama (Percentile 25)}
$$

$$
Q_3 = \text{Kuartil Ketiga (Percentile 75)}
$$

Nilai IQR dihitung menggunakan:

$$
IQR = Q_3 - Q_1
$$

Batas bawah dan batas atas ditentukan dengan:

$$
\text{Batas Bawah}
=
Q_1 - 1.5 \times IQR
$$

$$
\text{Batas Atas}
=
Q_3 + 1.5 \times IQR
$$

Data yang berada di luar batas tersebut dianggap sebagai *outlier*. Nilai *outlier* kemudian diubah menjadi `NaN` dan diisi kembali menggunakan interpolasi berbasis waktu.

---

## 3.2 Fungsi Cleaning dan Imputasi

```{code-cell} ipython3

def clean_and_impute_pollutant(
    df,
    pollutant_name
):

    # Membuat salinan data
    df_clean = df.copy()

    # Format tanggal
    df_clean['date'] = pd.to_datetime(
        df_clean['date']
    )

    # Urutkan berdasarkan tanggal
    df_clean = df_clean.sort_values(
        'date'
    ).reset_index(drop=True)

    # Parsing nilai polutan
    def parse_val(v):

        if pd.isna(v) or v is None:
            return np.nan

        s = (
            str(v)
            .replace('[', '')
            .replace(']', '')
            .strip()
        )

        if s.lower() in [
            'none',
            'nan',
            'null',
            ''
        ]:
            return np.nan

        try:
            return float(s)
        except:
            return np.nan

    df_clean[pollutant_name] = (
        df_clean[pollutant_name]
        .apply(parse_val)
    )

    # Interpolasi awal untuk missing value
    df_clean[pollutant_name] = (
        df_clean[pollutant_name]
        .interpolate(method='linear')
        .ffill()
        .bfill()
    )

    # Menghitung Q1 dan Q3
    Q1 = df_clean[pollutant_name].quantile(
        0.25
    )

    Q3 = df_clean[pollutant_name].quantile(
        0.75
    )

    # Menghitung IQR
    IQR = Q3 - Q1

    # Menentukan batas bawah dan atas
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Menentukan posisi outlier
    outlier_mask = (
        (df_clean[pollutant_name] < lower_bound)
        |
        (df_clean[pollutant_name] > upper_bound)
    )

    # Menghitung jumlah outlier
    jumlah_outlier = outlier_mask.sum()

    # Mengubah outlier menjadi NaN
    df_clean.loc[
        outlier_mask,
        pollutant_name
    ] = np.nan

    # Menggunakan tanggal sebagai index
    df_clean = df_clean.set_index(
        'date'
    )

    # Interpolasi berbasis waktu
    df_clean[pollutant_name] = (
        df_clean[pollutant_name]
        .interpolate(method='time')
        .ffill()
        .bfill()
    )

    # Mengubah menjadi array numerik
    signal = (
        df_clean[pollutant_name]
        .astype(float)
        .values
    )

    return (
        df_clean,
        signal,
        jumlah_outlier
    )
```

---

## 3.3 Eksekusi Preprocessing Ketiga Polutan

```{code-cell} ipython3

# Preprocessing CO
df_co_clean, signal_co, outlier_co = (
    clean_and_impute_pollutant(
        df_co_raw,
        'CO'
    )
)

# Preprocessing NO2
df_no2_clean, signal_no2, outlier_no2 = (
    clean_and_impute_pollutant(
        df_no2_raw,
        'NO2'
    )
)

# Preprocessing SO2
df_so2_clean, signal_so2, outlier_so2 = (
    clean_and_impute_pollutant(
        df_so2_raw,
        'SO2'
    )
)

print("=== HASIL PREPROCESSING ===")

print(
    f"CO  : {len(signal_co)} sampel | "
    f"{outlier_co} outlier"
)

print(
    f"NO2 : {len(signal_no2)} sampel | "
    f"{outlier_no2} outlier"
)

print(
    f"SO2 : {len(signal_so2)} sampel | "
    f"{outlier_so2} outlier"
)
```

---

# 4. Konsep Dasar Fitur Wavelet

Salah satu kelompok fitur yang dianalisis adalah fitur *wavelet*, khususnya:

* `wavelet_std`
* `wavelet_var`

Dekomposisi Wavelet atau **Discrete Wavelet Transform (DWT)** memecah sinyal deret waktu menjadi dua komponen utama:

1. **Koefisien Aproksimasi ($cA$)**
   Merepresentasikan komponen frekuensi rendah atau pola umum/tren sinyal.

2. **Koefisien Detail ($cD$)**
   Merepresentasikan perubahan atau fluktuasi pada frekuensi yang lebih tinggi.

Secara umum:

$$
X(t) \rightarrow cA + cD
$$

Dalam TSFEL, fitur `wavelet_std` dan `wavelet_var` digunakan untuk mengukur penyebaran koefisien hasil transformasi wavelet.

---

## 4.1 Wavelet Standard Deviation

Standar deviasi koefisien detail wavelet dapat dituliskan sebagai:

$$
\text{wavelet\_std}
=
\sqrt{
\frac{1}{N}
\sum_{i=1}^{N}
(cD_i-\mu_{cD})^2
}
$$

dengan:

$$
\mu_{cD}
=
\frac{1}{N}
\sum_{i=1}^{N}cD_i
$$

---

## 4.2 Wavelet Variance

Varians koefisien detail wavelet dihitung menggunakan:

$$
\text{wavelet\_var}
=
\frac{1}{N}
\sum_{i=1}^{N}
(cD_i-\mu_{cD})^2
$$

Nilai `wavelet_var` menunjukkan tingkat variasi koefisien detail wavelet, sedangkan `wavelet_std` menunjukkan standar deviasinya.

---

# 5. Perhitungan Manual & Validasi TSFEL

Untuk memahami cara kerja fitur wavelet digunakan contoh sinyal sederhana:

$$
X = [0.02, 0.04, 0.03, 0.05, 0.04]
$$

---

## 5.1 Dekomposisi Wavelet Haar

Dengan menggunakan *Haar Wavelet*:

$$
cD_1
=
\frac{0.02-0.04}{\sqrt{2}}
$$

$$
cD_1
\approx -0.014142
$$

Kemudian:

$$
cD_2
=
\frac{0.03-0.05}{\sqrt{2}}
$$

$$
cD_2
\approx -0.014142
$$

Sehingga diperoleh:

$$
cD =
[-0.014142,-0.014142]
$$

Karena kedua nilai koefisien detail tersebut sama, maka:

$$
\text{wavelet\_var}=0
$$

dan:

$$
\text{wavelet\_std}=0
$$

---

## 5.2 Pembuktian Menggunakan Python

```{code-cell} ipython3

# Sampel sinyal
x_sample = np.array([
    0.02,
    0.04,
    0.03,
    0.05,
    0.04
])

# Dekomposisi menggunakan PyWavelets
cA, cD = pywt.dwt(
    x_sample,
    'haar'
)

# Perhitungan manual/PyWavelets
manual_std = np.std(cD)
manual_var = np.var(cD)

# Perhitungan menggunakan TSFEL
tsfel_std = tsfel_features.wavelet_std(
    x_sample
)

tsfel_var = tsfel_features.wavelet_var(
    x_sample
)

print(
    "--- PEMBUKTIAN PERHITUNGAN FITUR WAVELET ---"
)

print(
    f"Koefisien Detail : {cD}"
)

print(
    f"Manual/PyWT -> "
    f"wavelet_std: {manual_std:.8f} | "
    f"wavelet_var: {manual_var:.8f}"
)

print(
    f"TSFEL Lib   -> "
    f"wavelet_std: {tsfel_std:.8f} | "
    f"wavelet_var: {tsfel_var:.8f}"
)
```

---

# 6. Ekstraksi 68 Fitur TSFEL

Setelah data melalui tahap preprocessing, dilakukan ekstraksi fitur menggunakan **Time Series Feature Extraction Library (TSFEL)**.

Sebanyak **68 fitur** diekstraksi dari masing-masing polutan, yaitu:

* CO
* $NO_2$
* $SO_2$

Dengan demikian jumlah fitur keseluruhan adalah:

$$
68 \times 3 = 204
$$

---

## 6.1 Daftar 68 Fitur TSFEL

```{code-cell} ipython3

FEATURE_LIST = """
abs_energy
auc
autocorr
average_power
calc_centroid
calc_max
calc_mean
calc_median
calc_min
calc_std
calc_var
dfa
distance
ecdf
ecdf_percentile
ecdf_percentile_count
ecdf_slope
entropy
fundamental_frequency
higuchi_fractal_dimension
hist_mode
human_range_energy
hurst_exponent
interq_range
kurtosis
lempel_ziv
lpcc
max_frequency
max_power_spectrum
maximum_fractal_length
mean_abs_deviation
mean_abs_diff
mean_diff
median_abs_deviation
median_abs_diff
median_diff
median_frequency
mfcc
mse
negative_turning
neighbourhood_peaks
petrosian_fractal_dimension
pk_pk_distance
positive_turning
power_bandwidth
rms
skewness
slope
spectral_centroid
spectral_decrease
spectral_distance
spectral_entropy
spectral_kurtosis
spectral_positive_turning
spectral_roll_off
spectral_roll_on
spectral_skewness
spectral_slope
spectral_spread
spectral_variation
spectrogram_mean_coeff
sum_abs_diff
wavelet_abs_mean
wavelet_energy
wavelet_entropy
wavelet_std
wavelet_var
zero_cross
""".split()

print(
    f"Jumlah fitur: {len(FEATURE_LIST)}"
)
```

---

## 6.2 Fungsi Konversi Hasil TSFEL Menjadi Scalar

Beberapa fungsi TSFEL dapat menghasilkan output berupa scalar, list, tuple, array, maupun dictionary. Oleh karena itu, hasil dikonversi menjadi satu nilai numerik.

```{code-cell} ipython3

def to_scalar(result):

    if result is None:
        return 0.0

    if (
        isinstance(result, dict)
        and "values" in result
    ):
        result = result["values"]

    if isinstance(
        result,
        (list, tuple, np.ndarray)
    ):

        arr = np.asarray(
            result,
            dtype=float
        )

        return (
            float(np.nanmean(arr))
            if len(arr) > 0
            else 0.0
        )

    try:
        return float(result)

    except Exception:
        return 0.0
```

---

## 6.3 Fungsi Ekstraksi Satu Fitur

```{code-cell} ipython3

def extract_single_feature(
    fn_name,
    signal,
    fs=1
):

    try:

        fn = getattr(
            tsfel_features,
            fn_name
        )

        params = inspect.signature(
            fn
        ).parameters

        if "fs" in params:

            result = fn(
                signal,
                fs
            )

        else:

            result = fn(
                signal
            )

        return to_scalar(
            result
        )

    except Exception as e:

        print(
            f"Gagal menghitung "
            f"{fn_name}: {e}"
        )

        return 0.0
```

---

# 7. Fungsi Ekstraksi Dataset TSFEL

Fungsi berikut digunakan untuk mengekstraksi seluruh 68 fitur dari satu sinyal polutan.

```{code-cell} ipython3

def generate_tsfel_dataset(
    signal_1d,
    output_csv_path,
    pollutant_name
):

    fs = 1

    row = {}

    for fn_name in FEATURE_LIST:

        row[fn_name] = (
            extract_single_feature(
                fn_name,
                signal_1d,
                fs
            )
        )

    df_tsfel = pd.DataFrame(
        [row]
    )

    df_tsfel.to_csv(
        output_csv_path,
        index=False
    )

    print(
        f"Berhasil! "
        f"{output_csv_path} "
        f"({df_tsfel.shape[1]} fitur) tersimpan."
    )

    return df_tsfel
```

---

# 8. Ekstraksi Fitur Ketiga Polutan

Proses ekstraksi kemudian dilakukan terhadap ketiga sinyal polutan.

```{code-cell} ipython3

# Ekstraksi fitur CO
df_co_tsfel = generate_tsfel_dataset(
    signal_co,
    "CO_Surabaya_Selatan_TSFEL.csv",
    "CO"
)

# Ekstraksi fitur NO2
df_no2_tsfel = generate_tsfel_dataset(
    signal_no2,
    "NO2_Surabaya_Selatan_TSFEL.csv",
    "NO2"
)

# Ekstraksi fitur SO2
df_so2_tsfel = generate_tsfel_dataset(
    signal_so2,
    "SO2_Surabaya_Selatan_TSFEL.csv",
    "SO2"
)
```

---

# 9. Pemeriksaan Hasil Ekstraksi

Setelah proses ekstraksi selesai, dilakukan pemeriksaan jumlah fitur yang dihasilkan.

```{code-cell} ipython3

print("=== HASIL EKSTRAKSI TSFEL ===")

print(
    f"CO  : {df_co_tsfel.shape[1]} fitur"
)

print(
    f"NO2 : {df_no2_tsfel.shape[1]} fitur"
)

print(
    f"SO2 : {df_so2_tsfel.shape[1]} fitur"
)

total_features = (
    df_co_tsfel.shape[1]
    + df_no2_tsfel.shape[1]
    + df_so2_tsfel.shape[1]
)

print(
    f"\nTotal fitur: {total_features}"
)
```

---

# 10. Penggabungan Menjadi Matriks 204 Fitur

Hasil ekstraksi dari ketiga polutan digabungkan menjadi satu matriks fitur.

Setiap polutan memiliki 68 fitur:

$$
68 + 68 + 68 = 204
$$

Prefix digunakan untuk membedakan fitur berdasarkan jenis polutan:

* `CO_`
* `NO2_`
* `SO2_`

```{code-cell} ipython3

# Tambahkan prefix CO
df_co_prefixed = df_co_tsfel.add_prefix(
    "CO_"
)

# Tambahkan prefix NO2
df_no2_prefixed = df_no2_tsfel.add_prefix(
    "NO2_"
)

# Tambahkan prefix SO2
df_so2_prefixed = df_so2_tsfel.add_prefix(
    "SO2_"
)

# Gabungkan ketiga dataframe
df_features_204 = pd.concat(
    [
        df_co_prefixed,
        df_no2_prefixed,
        df_so2_prefixed
    ],
    axis=1
)

print(
    "Ukuran matriks fitur:",
    df_features_204.shape
)

display(
    df_features_204.head()
)
```

---

# 11. Simpan Matriks 204 Fitur

Matriks fitur yang telah digabungkan disimpan dalam format CSV.

```{code-cell} ipython3

output_path = (
    "Surabaya_Selatan_204_Fitur_TSFEL.csv"
)

df_features_204.to_csv(
    output_path,
    index=False
)

print(
    f"File berhasil disimpan: "
    f"{output_path}"
)
```

---

# 12. Ringkasan Hasil Ekstraksi Fitur

Tabel berikut menampilkan beberapa fitur penting hasil ekstraksi TSFEL.

| Polutan | `abs_energy` | `entropy` | `calc_mean` | `calc_std` | `wavelet_std` | `wavelet_var` |
| :------ | -----------: | --------: | ----------: | ---------: | ------------: | ------------: |
| **CO**  |     0.305211 |  0.999358 |    0.028743 |   0.004120 |      0.000412 |      0.000000 |
| **NO2** |     125.4321 |  0.985412 |    18.52310 |   3.124510 |      0.812400 |      0.659994 |
| **SO2** |     0.000124 |  0.991204 |    0.000541 |   0.000112 |      0.000021 |      0.000000 |

> **Catatan:** Nilai pada tabel merupakan contoh format hasil. Nilai aktual yang digunakan dalam analisis diperoleh dari hasil eksekusi kode TSFEL terhadap dataset Surabaya Selatan.

---

# 13. Kesimpulan

Berdasarkan tahapan yang telah dilakukan, data kualitas udara wilayah **Surabaya Selatan** berhasil melalui proses preprocessing dan ekstraksi fitur deret waktu.

Tahap preprocessing dilakukan dengan mendeteksi *outlier* menggunakan metode **Interquartile Range (IQR)**. Nilai yang berada di luar batas IQR diubah menjadi `NaN`, kemudian dilakukan interpolasi berbasis waktu untuk mempertahankan kontinuitas data.

Selanjutnya, dilakukan ekstraksi fitur menggunakan **Time Series Feature Extraction Library (TSFEL)**. Sebanyak **68 fitur** diekstraksi untuk masing-masing polutan, yaitu **CO, $NO_2$, dan $SO_2$**.

Dengan tiga jenis polutan, jumlah keseluruhan fitur yang diperoleh adalah:

$$
68 \times 3 = 204
$$

Dengan demikian, diperoleh matriks yang terdiri dari **204 fitur numerik**.

Hasil akhir disimpan dalam file:

`Surabaya_Selatan_204_Fitur_TSFEL.csv`

Matriks 204 fitur tersebut selanjutnya dapat digunakan sebagai input untuk tahap **reduksi dimensi menggunakan PCA** dan **K-Means Clustering**.

```

Itu sudah **satu file Markdown panjang**. Jadi jangan membuat 2 file atau menggabungkan manual lagi—seluruh isi dalam blok di atas adalah isi dari **satu `.md`**.
```
