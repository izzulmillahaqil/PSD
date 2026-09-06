# 5. Kesimpulan

Berdasarkan pemrosesan data Sentinel-5P L2 menggunakan ekosistem **openEO**, penyimpanannya pada cloud database, hingga analisis statistik menggunakan **KNIME Analytics Platform**:

1. Ekstraksi data berbasis **GeoJSON** terbukti efisien dalam mengisolasi titik koordinat wilayah observasi spesifik tanpa perlu mengunduh keseluruhan *tile* satelit.
2. Analisis *time-series* dari September 2025 hingga Agustus 2026 memperlihatkan pola konsentrasi $NO_2$ yang dinamis, dengan pengaruh signifikan dari cuaca harian dan tingkat mobilitas wilayah.
3. Pembersihan data (*interpolation*) krusial dilakukan untuk menangani *missing values* akibat tutupan awan tebal pada data penginderaan jauh.
4. Integrasi pipeline data dari **Python** ke **PostgreSQL Aiven (Cloud Database)** dan ditarik ke **KNIME Analytics Platform** (menggunakan alur *PostgreSQL Connector $\rightarrow$ DB Table Selector $\rightarrow$ DB Reader $\rightarrow$ Statistics*) memudahkan proses eksplorasi statistik deskriptif secara terintegrasi.

---

## 📊 Analisis Statistik Deskriptif (KNIME Node Statistics)

Berikut adalah rangkuman nilai statistik deskriptif dari data *time-series* konsentrasi $NO_2$ ($mol/m^2$) hasil olahan node **Statistics** di KNIME:

| Metrik Statistics | Nilai | Keterangan Singkat |
| :--- | :--- | :--- |
| **Minimum** | `0.000006` | Konsentrasi $NO_2$ terendah harian |
| **Maximum** | `0.000233` | Konsentrasi $NO_2$ tertinggi harian |
| **Mean** | `0.000039` | Rata-rata konsentrasi $NO_2$ harian |
| **Median** | `0.000037` | Nilai tengah data $NO_2$ terurut |
| **Std. Deviation** | `0.000022` | Simpangan baku sebaran data |
| **Variance** | `4.84e-10` | Varians dari nilai data |
| **Skewness** | `3.82` | Distribusi miring positif (*right-skewed*) |
| **Kurtosis** | `21.45` | Leptokurtik (terdapat pencilan/lonjakan ekstrim) |

---

## 🧮 Penjelasan Fitur, Rumus, dan Contoh Perhitungan

Berikut adalah penjelasan setiap fitur metrik statistik pada node **Statistics** KNIME, beserta rumus matematika dan contoh perhitungannya:

### 1. Minimum ($\text{Min}$)
* **Penjelasan**: Nilai konsentrasi $NO_2$ paling rendah/minimum yang tercatat dalam rentang pengamatan.
* **Rumus**:
  $$\text{Min} = \min(x_1, x_2, \dots, x_n)$$
* **Contoh Hitung**:  
  Diberikan 3 sampel data $NO_2$: $[0.000015, 0.000032, 0.000048]$
  $$\text{Min} = 0.000015$$

---

### 2. Maximum ($\text{Max}$)
* **Penjelasan**: Nilai konsentrasi $NO_2$ paling tinggi/maksimum (puncak lonjakan polusi).
* **Rumus**:
  $$\text{Max} = \max(x_1, x_2, \dots, x_n)$$
* **Contoh Hitung**:  
  Dari sampel data $[0.000015, 0.000032, 0.000048]$
  $$\text{Max} = 0.000048$$

---

### 3. Mean ($\bar{x}$) — Rata-Rata
* **Penjelasan**: Rata-rata hitung nilai konsentrasi $NO_2$ dari seluruh periode observasi.
* **Rumus**:
  $$\bar{x} = \frac{\sum_{i=1}^{n} x_i}{n}$$
* **Contoh Hitung**:  
  Dari sampel data $[0.000015, 0.000032, 0.000048]$ dengan jumlah sampel $n = 3$:
  $$\bar{x} = \frac{0.000015 + 0.000032 + 0.000048}{3} = \frac{0.000095}{3} = 0.00003167$$

---

### 4. Median — Nilai Tengah
* **Penjelasan**: Nilai tengah data setelah seluruh sampel diurutkan dari terkecil ke terbesar. Metrik ini tahan terhadap pencilan (*outliers*).
* **Rumus**:
  $$\text{Median} = \text{Data ke-} \left(\frac{n + 1}{2}\right) \quad (\text{untuk } n \text{ ganjil})$$
* **Contoh Hitung**:  
  Data terurut $[0.000015, 0.000032, 0.000048]$ ($n=3$):
  $$\text{Median} = \text{Data ke-}2 = 0.000032$$

---

### 5. Standard Deviation ($s$) — Simpangan Baku
* **Penjelasan**: Mengukur seberapa besar penyimpangan nilai data konsentrasi $NO_2$ harian terhadap nilai rata-ratanya ($\bar{x}$).
* **Rumus**:
  $$s = \sqrt{\frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n - 1}}$$
* **Contoh Hitung**:  
  Dengan $\bar{x} = 0.00003167$ dan $n=3$:
  1. Selisih kuadrat tiap nilai terhadap $\bar{x}$:
     * $(0.000015 - 0.00003167)^2 = 2.779 \times 10^{-10}$
     * $(0.000032 - 0.00003167)^2 = 1.089 \times 10^{-13}$
     * $(0.000048 - 0.00003167)^2 = 2.666 \times 10^{-10}$
  2. Jumlah selisih kuadrat $= 5.446 \times 10^{-10}$
  3. Bagi dengan $(n - 1) = 2 \rightarrow 2.723 \times 10^{-10}$
  4. Akarkan hasilnya: $s = \sqrt{2.723 \times 10^{-10}} \approx 0.0000165$

---

### 6. Variance ($s^2$) — Varians
* **Penjelasan**: Kuadrat dari simpangan baku, menggambarkan sejauh mana nilai-nilai observasi menyebar dari rata-ratanya.
* **Rumus**:
  $$s^2 = \frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n - 1}$$
* **Contoh Hitung**:  
  Dari nilai $s = 0.0000165$:
  $$s^2 = (0.0000165)^2 \approx 2.72 \times 10^{-10}$$

---

### 7. Skewness — Kemiringan Distribusi
* **Penjelasan**: Mengukur ketidaksimetrisan kurva distribusi data. Nilai positif ($>0$) menunjukkan bahwa mayoritas konsentrasi $NO_2$ berada pada nilai rendah, namun terdapat beberapa kejadian lonjakan konsentrasi ekstrim (*right-skewed*).
* **Rumus**:
  $$\text{Skewness} = \frac{n}{(n-1)(n-2)} \sum_{i=1}^{n} \left(\frac{x_i - \bar{x}}{s}\right)^3$$

---

### 8. Kurtosis — Keruncingan Kurva
* **Penjelasan**: Mengukur derajat keruncingan puncak kurva distribusi. Nilai kurtosis yang tinggi menandakan keberadaan pencilan (*outliers*) ekstrim pada data harian $NO_2$.
* **Rumus**:
  $$\text{Kurtosis} = \left[ \frac{n(n+1)}{(n-1)(n-2)(n-3)} \sum_{i=1}^{n} \left(\frac{x_i - \bar{x}}{s}\right)^4 \right] - \frac{3(n-1)^2}{(n-2)(n-3)}$$