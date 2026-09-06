# 5. Kesimpulan

Berdasarkan pemrosesan data Sentinel-5P L2 menggunakan ekosistem **openEO**, penyimpanannya pada cloud database, hingga analisis statistik menggunakan **KNIME Analytics Platform**:

1. Ekstraksi data berbasis **GeoJSON** terbukti efisien dalam mengisolasi titik koordinat wilayah observasi spesifik tanpa perlu mengunduh keseluruhan *tile* satelit.
2. Analisis *time-series* dari September 2025 hingga Agustus 2026 memperlihatkan pola konsentrasi $NO_2$ yang dinamis, dengan pengaruh signifikan dari cuaca harian dan tingkat mobilitas wilayah.
3. Pembersihan data (*interpolation*) krusial dilakukan untuk menangani *missing values* akibat tutupan awan tebal pada data penginderaan jauh.
4. Integrasi pipeline data dari **Python** ke **PostgreSQL Aiven (Cloud Database)** dan ditarik ke **KNIME Analytics Platform** (menggunakan alur *PostgreSQL Connector $\rightarrow$ DB Table Selector $\rightarrow$ DB Reader $\rightarrow$ Statistics*) memudahkan proses eksplorasi statistik deskriptif secara terintegrasi.

---

## 🔬 Eksplorasi Metrik Statistika Deskriptif (KNIME)

Berikut adalah pembongkaran metrik statistik deskriptif dari data $NO_2$ hasil olahan node **Statistics** KNIME beserta kalkulasi interaktif dan interpretasi lingkungan:

```{note}
**Rangkuman Hasil KNIME**:
Data $NO_2$ yang dianalisis memiliki sifat *right-skewed* (miring kanan) dengan tingkat keruncingan (*kurtosis*) leptokurtik yang tinggi, mengindikasikan adanya kejadian ekstrim konsentrasi polutan harian pada periode tertentu.

```{tab-item} 1. Tendensi Sentral (Mean & Median)
### Rata-rata (Mean) vs Nilai Tengah (Median)

- **Mean ($\bar{x}$)**: Mengukur rata-rata aritmatika seluruh observasi harian.
  $$\bar{x} = \frac{\sum_{i=1}^{n} x_i}{n}$$
  
- **Median ($\text{Med}$)**: Nilai tengah yang membagi data terurut menjadi dua bagian sama besar (tahan terhadap pencilan).
  $$\text{Median} = \begin{cases} x_{\left(\frac{n+1}{2}\right)} & \text{jika } n \text{ ganjil} \\ \frac{x_{\left(\frac{n}{2}\right)} + x_{\left(\frac{n}{2}+1\right)}}{2} & \text{jika } n \text{ genap} \end{cases}$$

```{admonition} Contoh Kalkulasi
:class: tip
Misal sampel 3 hari data $NO_2$ ($mol/m^2$): $[0.000015, 0.000032, 0.000048]$
- **Mean**: $\frac{0.000015 + 0.000032 + 0.000048}{3} = \mathbf{0.00003167}$
- **Median**: Nilai posisi ke-2 = $\mathbf{0.000032}$

### Rentang Nilai Konsentrasi

- **Minimum ($\text{Min}$)**: Konsentrasi terendah harian, menggambarkan kondisi baseline kualitas udara saat bersih.
  $$\text{Min} = \min(x_1, x_2, \dots, x_n)$$

- **Maximum ($\text{Max}$)**: Konsentrasi puncak harian, menandakan titik tertinggi lonjakan polusi.
  $$\text{Max} = \max(x_1, x_2, \dots, x_n)$$

```{admonition} Interpretasi Lingkungan
:class: warning
Selisih antara $\text{Max}$ ($0.000233$) dan $\text{Min}$ ($0.000006$) menunjukkan rentang fluktuasi polusi yang tinggi, dipengaruhi oleh perubahan cuaca harian dan lonjakan aktivitas emisi lokal.

### Asimetri dan Pencilan (Outliers)

- **Skewness**: Ukuran kemiringan distribusi.
  $$\text{Skewness} = \frac{n}{(n-1)(n-2)} \sum_{i=1}^{n} \left(\frac{x_i - \bar{x}}{s}\right)^3$$

- **Kurtosis**: Ukuran keruncingan puncak kurva distribusi.
  $$\text{Kurtosis} = \left[ \frac{n(n+1)}{(n-1)(n-2)(n-3)} \sum_{i=1}^{n} \left(\frac{x_i - \bar{x}}{s}\right)^4 \right] - \frac{3(n-1)^2}{(n-2)(n-3)}$$

```{admonition} Analisis Lanjutan
:class: important
- **Skewness = 3.82 ($> 0$)**: Miring kanan (*Right-Skewed*). Menandakan mayoritas hari memiliki udara bersih/normal, namun terdapat hari-hari tertentu dengan lonjakan emisi polusi yang tinggi.
- **Kurtosis = 21.45 ($> 3$)**: Leptokurtik. Membuktikan adanya pencilan (*outliers*) ekstrim pada data harian $NO_2$.
