---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
---

# Business Understanding

## 1. Latar Belakang

Kualitas udara adalah indikator esensial bagi kesehatan publik dan kelestarian lingkungan. Seiring meningkatnya aktivitas warga, mobilitas transportasi, serta kegiatan ekonomi, risiko lonjakan gas polutan berbahaya di udara ikut membesar.

Tiga jenis gas polutan utama yang menjadi fokus pemantauan meliputi:

* **Nitrogen Dioksida ($NO_2$)**: Umumnya dipicu oleh emisi kendaraan bermotor dan operasional industri.
* **Karbon Monoksida ($CO$)**: Gas beracun yang bersumber dari proses pembakaran tidak sempurna.
* **Belerang Dioksida ($SO_2$)**: Polutan dari aktivitas vulkanik maupun pembakaran bahan bakar fosil.

## 2. Rumusan Masalah

Fokus utama dari analisis data ini ditujukan untuk menjawab pertanyaan berikut:

* Bagaimana pergerakan tren harian konsentrasi gas polutan ($NO_2$) di wilayah studi?
* Apakah ditemukan adanya siklus musiman, tren kenaikan jangka panjang, atau anomali lonjakan ekstrem pada tingkat polusi udara setempat?

## 3. Tujuan Proyek

Eksplorasi sains data ini dijalankan dengan tujuan:

* Membangun otomasi pengumpulan data citra satelit spasial (NetCDF) dan mentransformasikannya menjadi dataset tabular (CSV).
* Menjalankan Analisis Data Eksploratif (EDA) guna memahami karakteristik dan tren perubahan gas polutan dari waktu ke waktu.
* Menciptakan landasan data historis yang valid sebagai modal awal untuk keperluan pemodelan prediktif (*forecasting*).

## 4. Manfaat Proyek

* **Pemerintah & Pembuat Kebijakan**: Menyediakan *insight* berbasis data guna mendukung pengawasan emisi.
* **Masyarakat Umum**: Menjadi sarana informasi transparan untuk menumbuhkan kesadaran warga.
* **Akademisi & Praktisi Data**: Menjadi studi kasus nyata penerapan metodologi pengolahan data spasial ke pemodelan *Time Series*.