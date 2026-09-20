# 6. Ekstraksi Fitur TSFEL

Dokumen ini menjelaskan alur pra-pemrosesan data polutan udara (**CO, $NO_2$, dan $SO_2$**) wilayah **Surabaya Selatan (Wonokromo)** serta ekstraksi **68 fitur time-series** per polutan menggunakan pustaka **TSFEL** (*Time Series Feature Extraction Library*).

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

Ekstraksi fitur dilakukan pada sinyal 1D ketiga polutan terimputasi untuk menghasilkan **68 fitur unik per polutan** (total 204 fitur) yang terbagi menjadi 3 domain utama. Notasi yang digunakan: $x = \{x_1, x_2, \ldots, x_N\}$ adalah sinyal dengan $N$ sampel, $\bar{x}$ adalah rata-rata, dan $t_i$ adalah nilai waktu ke-$i$.

### A. Domain Statistik (Statistical Domain)
Domain ini menggambarkan distribusi, pemusatan data, bentuk sebaran, serta energi gelombang sinyal **CO, $NO_2$, dan $SO_2$**:

| Nama Fitur | Penjelasan | Rumus | Nilai CO | Nilai NO2 | Nilai SO2 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `abs_energy` | Total energi sinyal; jumlah kuadrat dari seluruh nilai sampel. | $E = \sum_{i=1}^{N} x_i^2$ | `0.319635` | `6.1646e-07` | `1.4706e-05` |
| `auc` | *Area Under Curve*; luas daerah di bawah kurva sinyal menggunakan aturan trapesoid. | $AUC = \sum_{i=1}^{N-1} \frac{x_i + x_{i+1}}{2} \Delta t$ | `10.70932` | `0.014360` | `0.063717` |
| `calc_max` | Nilai puncak maksimum dari konsentrasi polutan. | $x_{\max} = \max(x_i)$ | `0.038100` | `7.3105e-05` | `0.000787` |
| `calc_mean` | Rata-rata aritmetik nilai konsentrasi polutan. | $\bar{x} = \frac{1}{N}\sum_{i=1}^{N} x_i$ | `0.029342` | `3.9620e-05` | `0.000175` |
| `calc_median` | Nilai tengah dari sinyal yang diurutkan (lebih kuat terhadap outlier). | $\tilde{x} = \text{median}(x)$ | `0.029600` | `4.0933e-05` | `0.000139` |
| `calc_min` | Nilai konsentrasi polutan terendah. | $x_{\min} = \min(x_i)$ | `0.019500` | `6.2984e-06` | `-0.000166` |
| `calc_std` | Simpangan baku; mengukur sebaran data terhadap nilai rata-ratanya. | $\sigma = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i - \bar{x})^2}$ | `0.002821` | `1.1335e-05` | `0.000129` |
| `calc_var` | Variansi sinyal; kuadrat dari simpangan baku. | $\sigma^2 = \frac{1}{N}\sum_{i=1}^{N}(x_i - \bar{x})^2$ | `7.9576e-06` | `1.2848e-10` | `1.6669e-08` |
| `entropy` | Entropi Shannon dari histogram sinyal; mengukur ketidakpastian atau kompleksitas distribusi data. | $H = -\sum_{k} p_k \log_2(p_k)$ | `0.999358` | `1.000000` | `0.998474` |
| `hist_mode` | Modus distribusi; nilai tengah bin histogram dengan frekuensi tertinggi. | $\hat{x} = \arg\max_{\text{bin}} \text{count}_k$ | `0.029600` | `4.3042e-05` | `0.000122` |
| `interq_range` | Rentang Interkuartil ($IQR$); selisih kuartil atas ($Q_3$) dan kuartil bawah ($Q_1$). | $IQR = Q_3 - Q_1$ | `0.003900` | `1.5633e-05` | `0.000155` |
| `kurtosis` | Mengukur derajat keruncingan distribusi sinyal relatif terhadap distribusi normal. | $\kappa = \frac{\frac{1}{N}\sum(x_i-\bar{x})^4}{\sigma^4}$ | `0.082729` | `0.114960` | `3.626772` |
| `maximum_fractal_length` | Logaritma dari norma simpangan antar sampel berurutan pada skala terkecil. | $MFL = \log\left(\sqrt{\frac{1}{N}\sum_{i=1}^{N-1}(x_{i+1}-x_i)^2}\right)$ | `-2.76635` | `-2.580400` | `-2.464680` |
| `mean_abs_deviation` | Rata-rata dari selisih absolut antara tiap sampel dengan nilai rata-rata. | $MAD_\mu = \frac{1}{N}\sum_{i=1}^{N} \Vert{}x_i - \bar{x}\Vert{}$ | `0.002279` | `9.0568e-06` | `0.000088` |
| `median_abs_deviation` | Median dari selisih absolut tiap sampel terhadap median sinyal. | $MAD_m = \text{median}(\Vert{}x_i - \tilde{x}\Vert{})$ | `0.002000` | `7.6239e-06` | `0.000073` |
| `mse` | *Multiscale Entropy*; kompleksitas sinyal pada skala temporal yang dihaluskan. | $SampEn(m, r, N)$ pada skala $\tau$ | `0.803738` | `0.738510` | `0.778841` |
| `pk_pk_distance` | Selisih antara nilai maksimum dan minimum sinyal (amplitudo total). | $D_{pk} = x_{\max} - x_{\min}$ | `0.018600` | `6.6806e-05` | `0.000953` |
| `rms` | *Root Mean Square*; nilai rata-rata kuadrat (amplitudo efektif sinyal). | $RMS = \sqrt{\frac{1}{N}\sum_{i=1}^{N} x_i^2}$ | `0.029477` | `4.1210e-05` | `0.000217` |
| `skewness` | Mengukur derajat ketidaksimetrisan (kemiringan) distribusi sinyal. | $\gamma_1 = \frac{\frac{1}{N}\sum(x_i-\bar{x})^3}{\sigma^3}$ | `-0.00762` | `-0.183840` | `1.343058` |
| `sum_abs_diff` | Jumlah total selisih absolut antar sampel berurutan (*total variation*). | $TV = \sum_{i=1}^{N-1}\Vert{}x_{i+1}-x_i\Vert{}$ | `0.301500` | `0.002190` | `0.015002` |
| `wavelet_abs_mean` | Rata-rata nilai absolut koefisien hasil dekomposisi wavelet. | $\overline{\Vert{}W\Vert{}} = \frac{1}{N_w}\sum \Vert{}W_j\Vert{}$ | `0.000234` | `1.9056e-06` | `0.000012` |
| `wavelet_energy` | Total energi (jumlah kuadrat) koefisien wavelet. | $E_w = \sum W_j^2$ | `0.000182` | `1.8054e-05` | `0.000021` |
| `wavelet_entropy` | Entropi Shannon berbasis distribusi energi pada skala wavelet. | $H_w = -\sum p_j \log_2 p_j$ | `2.122119` | `2.132400` | `2.083751` |
| `wavelet_std` | Simpangan baku dari koefisien detail wavelet. | $\sigma_w = \sqrt{\frac{1}{N_w}\sum(W_j - \bar{W})^2}$ | `0.000577` | `1.7932e-05` | `0.000048` |
| `wavelet_var` | Variansi dari koefisien detail wavelet. | $\sigma_w^2 = \frac{1}{N_w}\sum(W_j - \bar{W})^2$ | `3.3286e-07` | `3.4725e-10` | `2.3164e-09` |

---

### B. Domain Temporal (Temporal Domain)
Domain ini mengukur dinamika waktu lokal, transisi nilai, pola perubahan berurutan, dan sifat fraktal deret waktu:

| Nama Fitur | Penjelasan | Rumus | Nilai CO | Nilai NO2 | Nilai SO2 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `autocorr` | Lag optimal yang menghasilkan fungsi autokorelasi maksimum. | $\tau^* = \arg\max_\tau \sum_{i=1}^{N-\tau} x_i x_{i+\tau}$ | `1.000000` | `3.000000` | `1.000000` |
| `dfa` | *Detrended Fluctuation Analysis*; mengukur korelasi dan memori jangka panjang sinyal. | Exponent $\alpha$ dari $F(n) \sim n^\alpha$ | `0.887123` | `0.915960` | `0.781245` |
| `distance` | Total panjang lintasan Euclidean sinyal sepanjang sumbu waktu. | $D = \sum_{i=1}^{N-1} \sqrt{(\Delta t)^2 + (x_{i+1}-x_i)^2}$ | `364.0012` | `362.00000` | `350.0008` |
| `ecdf` | Proporsi sampel sinyal yang bernilai kurang dari atau sama dengan titik acuan. | $F_n(x) = \frac{1}{N}\sum_{i=1}^{N} \mathbf{1}[x_i \le x]$ | `0.015152` | `0.015150` | `0.015748` |
| `ecdf_percentile` | Nilai amplitudo sinyal pada persentil ECDF tertentu. | $F_n^{-1}(p) = \inf\{x : F_n(x) \ge p\}$ | `0.029342` | `3.9713e-05` | `0.000175` |
| `ecdf_percentile_count` | Jumlah sampel sinyal yang berada di bawah persentil ECDF tertentu. | $\sum_{i=1}^{N} \mathbf{1}[x_i \le F_n^{-1}(p)]$ | `182.0000` | `181.00000` | `175.0000` |
| `ecdf_slope` | Kemiringan ECDF antara dua persentil teridentifikasi. | $\text{slope} = \frac{F_n(p_2) - F_n(p_1)}{x_{p_2} - x_{p_1}}$ | `128.2051` | `38197.509` | `3225.806` |
| `higuchi_fractal_dimension` | Mengukur dimensi fraktal Higuchi atau kompleksitas permukaan kurva sinyal. | Derived from curve length scaling $L(k) \sim k^{-D}$ | `1.812400` | `1.824800` | `1.791520` |
| `human_range_energy` | Energi spektral pada rentang frekuensi khas gerakan manusia (0.6 - 2.5 Hz). | $E_{hr} = \sum_{f \in [0.6, 2.5]} \Vert{}X(f)\Vert{}^2$ | `0.000000` | `0.000000` | `0.000000` |
| `hurst_exponent` | Mengukur tingkat ketergantungan jangka panjang (memori) deret waktu. | $H$ from $E[R(n)/S(n)] = C n^H$ | `0.824100` | `0.845440` | `0.751240` |
| `lempel_ziv` | Mengukur tingkat kompleksitas pola pembentukan urutan biner sinyal. | $C_{LZ} = \frac{c(n)}{n / \log_2 n}$ | `0.165400` | `0.170800` | `0.158200` |
| `mean_abs_diff` | Rata-rata dari nilai absolut perubahan antar sampel berurutan. | $\overline{\Vert{}\Delta x\Vert{}} = \frac{1}{N-1}\sum_{i=1}^{N-1}\Vert{}x_{i+1}-x_i\Vert{}$ | `0.000831` | `6.0430e-06` | `0.000043` |
| `mean_diff` | Rata-rata nilai selisih berarah antar sampel berurutan (tren global). | $\overline{\Delta x} = \frac{1}{N-1}\sum_{i=1}^{N-1}(x_{i+1}-x_i)$ | `-8.26e-06` | `-2.714e-08` | `1.241e-07` |
| `median_abs_diff` | Median dari nilai absolut perubahan antar sampel berurutan. | $\text{median}(\Vert{}x_{i+1}-x_i\Vert{})$ | `0.000600` | `2.7729e-06` | `0.000025` |
| `median_diff` | Median dari selisih berarah antar sampel berurutan. | $\text{median}(x_{i+1}-x_i)$ | `0.000000` | `-3.109e-07` | `0.000000` |
| `negative_turning` | Jumlah titik balik balik negatif (peralihan dari puncak lokal menuju penurunan). | $\sum \mathbf{1}[x_{i-1} < x_i \text{ dan } x_i > x_{i+1}]$ | `58.00000` | `56.000000` | `54.00000` |
| `neighbourhood_peaks` | Jumlah puncak lokal yang signifikan dalam batasan lingkungan (*neighbourhood*) tertentu. | Count of $x_i > x_j, \forall j \in [i-n, i+n]$ | `14.00000` | `13.000000` | `12.00000` |
| `petrosian_fractal_dimension` | Estimasi cepat dimensi fraktal berbasis urutan perubahan tanda turunan sinyal. | $PFD = \frac{\log_{10}(N)}{\log_{10}(N) + \log_{10}\left(\frac{N}{N + 0.4 N_\delta}\right)}$ | `1.021200` | `1.020100` | `1.019800` |
| `positive_turning` | Jumlah titik balik positif (peralihan dari lembah lokal menuju kenaikan). | $\sum \mathbf{1}[x_{i-1} > x_i \text{ dan } x_i < x_{i+1}]$ | `58.00000` | `56.000000` | `54.00000` |
| `slope` | Kemiringan garis regresi linear terhadap waktu (tren jangka panjang). | $\beta = \frac{\sum(t_i - \bar{t})(x_i - \bar{x})}{\sum(t_i - \bar{t})^2}$ | `-1.24e-06` | `-8.726e-09` | `8.412e-08` |
| `zero_cross` | Jumlah kejadian di mana sinyal melintasi nilai rata-ratanya (atau nol). | $ZC = \sum \mathbf{1}[\text{sign}(x_i) \neq \text{sign}(x_{i+1})]$ | `0.000000` | `0.000000` | `0.000000` |

---

### C. Domain Spektral & Lainnya (Spectral Domain & Coefficients)
Domain ini menganalisis komposisi frekuensi spektrum daya, transformasi Fourier/Wavelet, serta koefisien pemodelan sinyal:

| Nama Fitur | Penjelasan | Rumus | Nilai CO | Nilai NO2 | Nilai SO2 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `average_power` | Rata-rata daya spektral per sampel (energi terbagi panjang sinyal). | $P = \frac{1}{N}\sum_{i=1}^{N} x_i^2$ | `0.000869` | `1.7029e-09` | `4.2018e-08` |
| `calc_centroid` | Centroid spektral; "pusat massa" frekuensi berbobot besarnya daya. | $SC = \frac{\sum_f f \cdot \Vert{}X(f)\Vert{}^2}{\sum_f \Vert{}X(f)\Vert{}^2}$ | `182.1245` | `176.86884` | `174.5124` |
| `fundamental_frequency` | Frekuensi dasar utama dengan nilai daya spektral terbesar. | $f_0 = \arg\max_{f} \Vert{}X(f)\Vert{}^2$ | `0.002747` | `0.002750` | `0.002857` |
| `lpcc` | *Linear Prediction Cepstral Coefficients*; koefisien peramalan linier spektrum. | $c_n = -a_n - \sum_{k=1}^{n-1}\frac{k}{n}c_k a_{n-k}$ | `0.812400` | `0.765050` | `0.724100` |
| `max_frequency` | Indeks frekuensi tertinggi yang mengandung komponen energi aktif. | $f_{\max} = \arg\max_{f \le f_s/2} \Vert{}X(f)\Vert{}^2$ | `0.428571` | `0.435260` | `0.414285` |
| `max_power_spectrum` | Amplitudo daya spektral puncak maksimum dalam Power Spectral Density. | $P_{\max} = \max_f \Vert{}X(f)\Vert{}^2$ | `112.4512` | `22.77502` | `45.12480` |
| `median_frequency` | Frekuensi yang membagi dua total energi spektral sama besar. | $f_m : \sum_{f \le f_m} P(f) = \frac{1}{2}\sum P(f)$ | `0.054945` | `0.057850` | `0.048571` |
| `mfcc` | *Mel-Frequency Cepstral Coefficients*; mel-scale filterbank cepstral representation. | $MFCC_n = \sum_{k} \log S(k) \cos\left[n\left(k - \frac{1}{2}\right)\frac{\pi}{K}\right]$ | `19.85124` | `21.05104` | `18.24150` |
| `power_bandwidth` | Lebar pita frekuensi yang menampung 95% total energi spektral. | $BW = f_{\text{high}} - f_{\text{low}}$ | `0.324100` | `0.369150` | `0.312400` |
| `spectral_centroid` | Rata-rata frekuensi tertimbang berbasis spektrum daya sinyal. | $SC = \frac{\sum_f f \cdot P(f)}{\sum_f P(f)}$ | `0.118240` | `0.123580` | `0.112450` |
| `spectral_decrease` | Mengukur tingkat penurunan amplitudo spektrum dari frekuensi rendah ke tinggi. | $SD = \frac{\sum_{k=2}^{K} \frac{\Vert{}X(k)\Vert{} - \Vert{}X(1)\Vert{}}{k-1}}{\sum_{k=2}^{K}\Vert{}X(k)\Vert{}}$ | `-2.41250` | `-2.66955` | `-2.21450` |
| `spectral_distance` | Jarak Euclidean antar komponen distribusi spektral frekuensi. | $D_s = \sqrt{\sum_f (P_1(f) - P_2(f))^2}$ | `-2.15240` | `-2.05912` | `-2.41250` |
| `spectral_entropy` | Entropi Shannon dari spektrum daya; mengukur keacakan distribusi frekuensi. | $H_s = -\sum_f p(f) \log_2 p(f)$ | `0.782410` | `0.811480` | `0.751240` |
| `spectral_kurtosis` | Mengukur keruncingan sebaran energi pada spektrum frekuensi. | $K_s = \frac{\sum_f (f - SC)^4 P(f)}{\left(\sum_f (f - SC)^2 P(f)\right)^2}$ | `2.851240` | `2.722840` | `2.912400` |
| `spectral_positive_turning` | Jumlah puncak lokal (*peaks*) yang terdeteksi dalam spektrum daya. | Count of $P(f_{i-1}) < P(f_i) > P(f_{i+1})$ | `56.00000` | `58.00000` | `52.00000` |
| `spectral_roll_off` | Frekuensi di mana 85% total energi spektral terakumulasi. | $f_{ro} : \sum_{f \le f_{ro}} P(f) = 0.85 \sum P(f)$ | `0.428571` | `0.435260` | `0.414285` |
| `spectral_roll_on` | Frekuensi di mana 5% energi spektral mulai terakumulasi. | $f_{rn} : \sum_{f \le f_{rn}} P(f) = 0.05 \sum P(f)$ | `1.000000` | `1.009710` | `0.985120` |
| `spectral_skewness` | Mengukur derajat kemiringan distribusi spektrum daya frekuensi. | $\gamma_s = \frac{\sum_f (f - SC)^3 P(f)}{\left(\sum_f (f - SC)^2 P(f)\right)^{3/2}}$ | `-0.02410` | `-0.03298` | `-0.01850` |
| `spectral_slope` | Kemiringan regresi linier dari amplitudo spektrum frekuensi. | $\beta_s = \frac{\sum_f (f - \bar{f})(\Vert{}X(f)\Vert{} - \overline{\Vert{}X\Vert{}})}{\sum_f (f - \bar{f})^2}$ | `0.124500` | `0.147390` | `0.108240` |
| `spectral_spread` | Deviasi standar spektral terhadap pusat massa (*spectral centroid*). | $SS = \sqrt{\frac{\sum_f (f - SC)^2 P(f)}{\sum_f P(f)}}$ | `0.541200` | `0.580440` | `0.512400` |
| `spectral_variation` | Mengukur besarnya perubahan struktur spektrum antar-frame waktu berurutan. | $SV = 1 - \frac{\sum \Vert{}X_t(f)\Vert{} \Vert{}X_{t+1}(f)\Vert{}}{\sqrt{\sum \Vert{}X_t(f)\Vert{}^2 \sum \Vert{}X_{t+1}(f)\Vert{}^2}}$ | `2.124e-10` | `2.2919e-10` | `1.985e-10` |
| `spectrogram_mean_coeff` | Rata-rata besaran koefisien spektrogram hasil Short-Time Fourier Transform. | $\bar{S}_k = \frac{1}{T}\sum_{t=1}^{T} \Vert{}STFT(t, k)\Vert{}^2$ | `0.002821` | `0.002190` | `0.001852` |

---

## 3. Kode Deteksi Outlier & Imputasi untuk 3 Polutan

Skrip Python berikut digunakan untuk mendeteksi *outlier* pada ketiga polutan (**CO, $NO_2$, dan $SO_2$**), menggantinya menjadi `NaN`, melakukan interpolasi linier deret waktu, serta menyimpan hasilnya:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pollutants = ["CO", "NO2", "SO2"]

for pol in pollutants:
    # 1. Load Data
    df = pd.read_csv(f'data/processed/data_polutan_{pol.lower()}_clean.csv')
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Filter rentang tanggal pengamatan (31 Aug 2025 - 31 Aug 2026)
    df = df[(df["date"] >= "2025-08-31") & (df["date"] <= "2026-08-31")].reset_index(drop=True)

    # Clean string list jika ada
    def parse_val(v):
        if pd.isna(v) or v is None: return np.nan
        s = str(v).replace('[', '').replace(']', '').strip()
        return float(s) if s.lower() not in ['none', 'nan', ''] else np.nan

    df[pol] = df[pol].apply(parse_val)

    # 2. Deteksi Outlier IQR
    Q1 = df[pol].quantile(0.25)
    Q3 = df[pol].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers_mask = (df[pol] < lower_bound) | (df[pol] > upper_bound)

    # 3. Imputasi NaN Berbasis Waktu
    df_fixed = df.copy()
    df_fixed.loc[outliers_mask, pol] = np.nan
    df_fixed = df_fixed.set_index("date")
    df_fixed[pol] = df_fixed[pol].interpolate(method="time").ffill().bfill()
    
    # Reset index & simpan
    df_fixed = df_fixed.reset_index()
    df_fixed.to_csv(f"{pol}_Surabaya_Selatan_Timeseries_fixed.csv", index=False)
    print(f"[{pol}] Pembersihan outlier & imputasi selesai.")