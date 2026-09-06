# 5. Kesimpulan

Berdasarkan pemrosesan data Sentinel-5P L2 menggunakan ekosistem **openEO**, penyimpanannya pada cloud database, hingga analisis statistik menggunakan **KNIME Analytics Platform**, dapat disimpulkan bahwa:

1. Ekstraksi data berbasis **GeoJSON** terbukti efisien dalam mengisolasi titik koordinat wilayah observasi spesifik tanpa perlu mengunduh keseluruhan *tile* satelit.
2. Analisis *time-series* dari September 2025 hingga Agustus 2026 memperlihatkan pola konsentrasi $NO_2$ yang dinamis, dengan kemungkinan pengaruh dari kondisi cuaca dan tingkat aktivitas atau mobilitas wilayah.
3. Pembersihan data (*interpolation*) diperlukan untuk menangani *missing values* yang dapat terjadi akibat keterbatasan observasi pada data penginderaan jauh, termasuk pengaruh kondisi atmosfer dan tutupan awan.
4. Integrasi pipeline data dari **Python** ke **PostgreSQL Aiven (Cloud Database)** kemudian ditarik ke **KNIME Analytics Platform** menggunakan alur **PostgreSQL Connector $\rightarrow$ DB Table Selector $\rightarrow$ DB Reader $\rightarrow$ Statistics** memudahkan proses eksplorasi statistik deskriptif secara terintegrasi.

---

## 🔬 Eksplorasi Metrik Statistika Deskriptif (KNIME)

Berikut merupakan penjelasan metrik statistik deskriptif dari data $NO_2$ hasil pengolahan menggunakan node **Statistics** pada KNIME, beserta contoh kalkulasi dan interpretasinya.

```{note}
**Rangkuman Hasil KNIME**:
Data $NO_2$ yang dianalisis menunjukkan distribusi yang **right-skewed** atau miring ke kanan. Nilai skewness yang tinggi menunjukkan adanya beberapa observasi dengan konsentrasi $NO_2$ yang jauh lebih tinggi dibandingkan sebagian besar observasi lainnya.