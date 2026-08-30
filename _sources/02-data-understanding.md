# 2. Data Understanding

Tahap ini berfokus pada pengenalan spesifikasi dataset hasil crawling dan analisis terhadap fitur-fitur yang didapatkan dari sensor satelit Sentinel-5P.

## Deskripsi Polutan

Satelit memonitor berbagai polutan berbahaya di troposfer bumi. Dua yang paling umum menjadi indikator kualitas udara adalah **CO** dan **NO2**:

* **Apa itu CO (Karbon Monoksida)?**
  CO adalah gas beracun yang tidak berwarna, tidak berbau, dan tidak berasa. Gas ini utamanya dihasilkan dari proses pembakaran bahan bakar fosil yang tidak sempurna. Sumber terbesarnya adalah asap knalpot kendaraan bermotor. Jika terhirup dalam jumlah banyak, CO sangat berbahaya karena akan mengikat hemoglobin dalam darah dan menghalangi suplai oksigen ke tubuh.

* **Apa itu NO2 (Nitrogen Dioksida)?**
  NO2 adalah gas beracun berwarna coklat kemerahan dengan bau yang tajam dan menyengat. Berbeda dengan CO, NO2 dihasilkan dari pembakaran bahan bakar fosil pada suhu tinggi, seperti mesin diesel kendaraan berat, kapal laut, dan aktivitas industri/pembangkit listrik. Pada proyek ini, NO2 dipilih sebagai fitur utama karena area pengamatan merupakan jalur padat lalu lintas dan aktivitas industri.

## Eksplorasi Fitur (Dataset)

Data yang diunduh (disimpan dalam `data_polutan_no2_clean.csv`) memiliki dua fitur utama:

1. **Tanggal (Date)**: Menunjukkan waktu observasi satelit dalam rentang 1 September 2025 hingga 31 Agustus 2026 (resolusi harian).
2. **Konsentrasi NO2**: Nilai kepadatan partikel polutan NO2 di udara area observasi, diukur menggunakan satuan ukur $\text{mol/m}^2$.

## Apakah Ada Data Aneh (Anomali)?

Dalam data time-series kualitas udara, beberapa data aneh (*outliers*) atau nilai hilang (*missing values*) dapat muncul akibat:
* **Tutup Tutupan Awan (Cloud Cover)**: Sensor satelit optic/troposfer terkadang terhalang awan tebal sehingga menghasilkan data bernilai *NaN* atau `0`.
* **Lonjakan Ekstrem (Spike)**: Terjadi pada hari-hari tertentu akibat peningkatan emisi mendadak (misal: kemacetan parah saat musim mudik/liburan) atau gangguan teknik pada sensor satelit.