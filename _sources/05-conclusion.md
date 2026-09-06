# 5. Kesimpulan & Penjelasan Metrik Statistika Deskriptif

Berdasarkan pemrosesan data Sentinel-5P L2 menggunakan ekosistem **openEO**, penyimpanannya pada cloud database, hingga analisis statistik menggunakan **KNIME Analytics Platform**, dapat disimpulkan bahwa:

1. Ekstraksi data berbasis **GeoJSON** terbukti efisien dalam mengisolasi titik koordinat wilayah observasi spesifik tanpa perlu mengunduh keseluruhan *tile* satelit.

2. Analisis *time-series* dari September 2025 hingga Agustus 2026 memperlihatkan pola konsentrasi $NO_2$ yang dinamis, dengan kemungkinan pengaruh dari kondisi cuaca dan tingkat aktivitas atau mobilitas wilayah.

3. Pembersihan data (*interpolation*) diperlukan untuk menangani *missing values* yang dapat terjadi akibat keterbatasan observasi pada data penginderaan jauh, termasuk pengaruh kondisi atmosfer dan tutupan awan.

4. Integrasi pipeline data dari **Python** ke **PostgreSQL Aiven (Cloud Database)** kemudian ditarik ke **KNIME Analytics Platform** menggunakan alur **PostgreSQL Connector $\rightarrow$ DB Table Selector $\rightarrow$ DB Reader $\rightarrow$ Statistics** memudahkan proses eksplorasi statistik deskriptif secara terintegrasi.

---

## Pembongkaran Metrik Statistika Deskriptif

Berikut merupakan penjelasan detail setiap metrik statistik deskriptif dari data konsentrasi $NO_2$ hasil pengolahan node **Statistics** pada KNIME, lengkap dengan rumus matematika, kalkulasi, dan interpretasinya.

```{note}
**Ringkasan Hasil Evaluasi KNIME**:

Data $NO_2$ yang dianalisis menunjukkan bentuk distribusi **right-skewed** (miring kanan) serta nilai kurtosis bertipe **leptokurtik**. Hal ini menandakan bahwa pada sebagian besar hari, konsentrasi $NO_2$ berada pada tingkat normal/rendah, namun terdapat beberapa periode harian yang mengalami lonjakan konsentrasi polutan secara signifikan.
```

### 1. Min (Minimum)

- **Penjelasan**: Nilai terkecil dari seluruh observasi konsentrasi $NO_2$ harian pada wilayah pengamatan.

- **Rumus**:

  $$
  \text{Min} = \min(x_1, x_2, \dots, x_n)
  $$

- **Contoh Kalkulasi**:

  Diberikan 3 sampel data konsentrasi $NO_2$ ($mol/m^2$):

  $$
  [0.000015, 0.000032, 0.000048]
  $$

  $$
  \text{Min} = 0.000015
  $$

### 2. Max (Maximum)

- **Penjelasan**: Nilai puncak/tertinggi dari konsentrasi $NO_2$ yang tercatat selama rentang waktu observasi.

- **Rumus**:

  $$
  \text{Max} = \max(x_1, x_2, \dots, x_n)
  $$

- **Contoh Kalkulasi**:

  Dari sampel data:

  $$
  [0.000015, 0.000032, 0.000048]
  $$

  $$
  \text{Max} = 0.000048
  $$

### 3. Mean (Rata-Rata Aritmatika)

- **Penjelasan**: Nilai rata-rata hitung konsentrasi $NO_2$ harian yang memberikan gambaran umum kondisi kualitas udara secara keseluruhan.

- **Rumus**:

  $$
  \bar{x} = \frac{\sum_{i=1}^{n} x_i}{n}
  $$

- **Contoh Kalkulasi**:

  Dari sampel data $[0.000015, 0.000032, 0.000048]$ dengan $n = 3$:

  $$
  \bar{x}
  =
  \frac{0.000015 + 0.000032 + 0.000048}{3}
  =
  0.00003167
  $$

### 4. Median (Nilai Tengah)

- **Penjelasan**: Nilai yang berada tepat di tengah-tengah set data setelah diurutkan. Metrik ini sangat andal karena tidak terpengaruh oleh pencilan (*outliers*).

- **Rumus**:

  $$
  \text{Median}
  =
  \text{Data ke-}
  \left(
  \frac{n + 1}{2}
  \right)
  \quad
  (\text{untuk } n \text{ ganjil})
  $$

- **Contoh Kalkulasi**:

  Data terurut $[0.000015, 0.000032, 0.000048]$ dengan $n = 3$:

  $$
  \text{Median} = 0.000032
  $$

### 5. Standard Deviation (Simpangan Baku)

- **Penjelasan**: Ukuran standar seberapa jauh nilai-nilai konsentrasi $NO_2$ harian menyimpang atau tersebar dari nilai rata-ratanya.

- **Rumus**:

  $$
  s =
  \sqrt{
  \frac{
  \sum_{i=1}^{n}(x_i-\bar{x})^2
  }{
  n-1
  }
  }
  $$

- **Contoh Kalkulasi**:

  Dengan $\bar{x} = 0.00003167$ dan $n = 3$:

  1. Hitung selisih kuadrat:

     $$
     (0.000015-\bar{x})^2
     +
     (0.000032-\bar{x})^2
     +
     (0.000048-\bar{x})^2
     =
     5.446 \times 10^{-10}
     $$

  2. Bagi dengan $(n-1)=2$:

     $$
     \frac{5.446 \times 10^{-10}}{2}
     =
     2.723 \times 10^{-10}
     $$

  3. Akarkan nilainya:

     $$
     s
     =
     \sqrt{2.723 \times 10^{-10}}
     \approx
     0.0000165
     $$

### 6. Variance (Varians)

- **Penjelasan**: Nilai kuadrat dari simpangan baku ($s^2$) yang menggambarkan besarnya variabilitas atau keragaman data $NO_2$.

- **Rumus**:

  $$
  s^2
  =
  \frac{
  \sum_{i=1}^{n}(x_i-\bar{x})^2
  }{
  n-1
  }
  $$

- **Contoh Kalkulasi**:

  Dari $s = 0.0000165$:

  $$
  s^2
  =
  (0.0000165)^2
  =
  2.723 \times 10^{-10}
  $$

### 7. Skewness (Kemiringan Distribusi)

- **Penjelasan**: Mengukur derajat ketidaksimetrisan kurva distribusi data.

  - **Analisis Data ($NO_2$)**: Nilai Skewness $= 3.82$ ($> 0$), mengindikasikan kurva miring ke kanan (*right-skewed*). Sebagian besar observasi bernilai rendah, namun terdapat beberapa ekor data bernilai tinggi.

- **Rumus**:

  $$
  \text{Skewness}
  =
  \frac{n}{(n-1)(n-2)}
  \sum_{i=1}^{n}
  \left(
  \frac{x_i-\bar{x}}{s}
  \right)^3
  $$

### 8. Kurtosis (Keruncingan Kurva)

- **Penjelasan**: Mengukur tingkat keruncingan puncak distribusi data dibandingkan dengan distribusi normal.

  - **Analisis Data ($NO_2$)**: Nilai Kurtosis $= 21.45$ ($> 3$), tergolong *leptokurtik*. Hal ini menunjukkan adanya ekor distribusi yang tebal akibat keberadaan nilai-nilai ekstrem (*outliers*) pada hari tertentu.

- **Rumus**:

  $$
  \text{Kurtosis}
  =
  \left[
  \frac{
  n(n+1)
  }{
  (n-1)(n-2)(n-3)
  }
  \sum_{i=1}^{n}
  \left(
  \frac{x_i-\bar{x}}{s}
  \right)^4
  \right]
  -
  \frac{
  3(n-1)^2
  }{
  (n-2)(n-3)
  }
  $$