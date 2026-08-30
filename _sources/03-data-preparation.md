# 3. Data Preparation

Tahap ini mencakup proses pembersihan (*cleaning*), pemrosesan awal (*preprocessing*), dan pemformatan data hasil *crawling* agar siap digunakan dalam analisis *time-series*.

## Alur Pemrosesan Data

Proses penyiapan data dilakukan melalui beberapa tahapan berikut:

1. **Filtering Area Koordinat (GeoJSON)**:
   Membatasi area pengambilan data polutan menggunakan file `Wilayah.geojson` untuk memastikan data yang diambil presisi sesuai wilayah observasi.

2. **Ekstraksi Data Terkini**:
   Mengambil data historis konsentrasi polutan ($NO_2$) dari rentang waktu **1 September 2025 hingga 31 Agustus 2026** menggunakan resolusi harian.

3. **Handling Missing Values & Anomali**:
   * Melakukan identifikasi nilai kosong (*NaN*) yang disebabkan oleh tutupan awan (*cloud cover*) pada pengamatan satelit.
   * Menerapkan teknik *interpolation* (atau *forward-fill*) untuk mengisi gap data harian yang hilang.

4. **Ekspor ke Format CSV**:
   Menyimpan hasil data yang telah dibersihkan ke dalam file `data_polutan_no2_clean.csv` di folder `data/processed/`.

## Struktur Dataset Akhir

Dataset hasil pemrosesan memiliki struktur sebagai berikut:

| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `Date` | Datetime (`YYYY-MM-DD`) | Tanggal pengambilan data observasi satelit |
| `NO2_concentration` | Float | Konsentrasi polutan $NO_2$ ($\text{mol/m}^2$) |