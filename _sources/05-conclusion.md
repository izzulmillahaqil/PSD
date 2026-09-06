# 5. Kesimpulan

Berdasarkan pemrosesan data Sentinel-5P L2 menggunakan ekosistem **openEO**, penyimpanannya pada cloud database, hingga analisis statistik menggunakan **KNIME Analytics Platform**:

1. Ekstraksi data berbasis **GeoJSON** terbukti efisien dalam mengisolasi titik koordinat wilayah observasi spesifik tanpa perlu mengunduh keseluruhan *tile* satelit.
2. Analisis *time-series* dari September 2025 hingga Agustus 2026 memperlihatkan pola konsentrasi $NO_2$ yang dinamis, dengan pengaruh signifikan dari cuaca harian dan tingkat mobilitas wilayah.
3. Pembersihan data (*interpolation*) krusial dilakukan untuk menangani *missing values* akibat tutupan awan tebal pada data penginderaan jauh.
4. Integrasi pipeline data dari **Python** ke **PostgreSQL Aiven (Cloud Database)** dan ditarik ke **KNIME Analytics Platform** (menggunakan alur *PostgreSQL Connector $\rightarrow$ DB Table Selector $\rightarrow$ DB Reader $\rightarrow$ Statistics*) memudahkan proses eksplorasi statistik deskriptif secara terintegrasi.

---

##  Analisis Statistik Deskriptif (KNIME Node Statistics)

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

