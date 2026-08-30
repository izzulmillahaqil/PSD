# 1. Business Understanding

Tahap ini bertujuan untuk memahami konteks masalah, menentukan fokus observasi, serta mengidentifikasi manfaat analisis kualitas udara berbasis data satelit.

## Latar Belakang & Tujuan Proyek
Kualitas udara merupakan salah satu faktor penting yang mempengaruhi kesehatan masyarakat dan lingkungan. Pada proyek ini, analisis dilakukan untuk memantau konsentrasi polutan udara di wilayah observasi menggunakan data penginderaan jauh (*remote sensing*) dari sensor satelit **Sentinel-5P**.

Tujuan utama dari tugas ini adalah:
1. **Memantau Tren Kualitas Udara**: Mengetahui fluktuasi tingkat polusi udara dari waktu ke waktu secara *time-series* (periode 1 September 2025 hingga 31 Agustus 2026).
2. **Identifikasi Area Berisiko**: Membatasi area observasi spesifik menggunakan boundary **GeoJSON** untuk mendapatkan presisi lokasi yang akurat.
3. **Mendukung Keputusan Berbasis Data**: Menyediakan visualisasi data yang transparan untuk diunggah pada web statis agar mudah diakses.

## Manfaat Analisis
Hasil analisis dari proyek ini memberikan berbagai manfaat praktis:

* **Bagi Masyarakat**: Menghasilkan kesadaran (*awareness*) mengenai kondisi udara lokal sehingga dapat mengambil tindakan pencegahan saat terjadi lonjakan polusi.
* **Bagi Pemerintah & Pengambil Kebijakan**: Menjadi acuan awal dalam perancangan regulasi emisi, tata ruang wilayah, dan evaluasi dampak sektor transportasi/industri.
* **Bagi Akademisi/Peneliti**: Menjadi dokumentasi dan dasar riset lebih lanjut dalam memodelkan pola penyebaran polutan udara regional.