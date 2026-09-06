# Implementasi Analisis Data Polutan: Dari Cloud Database ke KNIME

Panduan ini menguraikan tahapan-tahapan untuk menghubungkan database PostgreSQL di platform **Aiven Cloud**, melakukan verifikasi koneksi, serta mengekstraksi metrik statistika deskriptif memanfaatkan **KNIME Analytics Platform**.

---

## Langkah 1: Memperoleh Kredensial Database dari Aiven

Sebelum menyambungkan koneksi melalui aplikasi atau skrip analitik apa pun, kita membutuhkan informasi kredensial server PostgreSQL dari dashboard Aiven.

1. Akses console/dashboard **Aiven**, lalu buka proyek yang dimiliki.
2. Buka tab **Overview** pada layanan PostgreSQL yang sedang beroperasi (`pg-3aba66e5`).
3. Pada bagian **Connection information**, catat parameter-parameter berikut:
   * **Host**: `pg-3aba66e5-izzulmillahaqil.e.aivencloud.com`
   * **Port**: `21121`
   * **Database name**: `defaultdb`
   * **User**: `avnadmin`
   * **Password**: *(Salin dari ikon mata / tombol copy)*
   * **SSL mode**: `require`

---

## Langkah 2: Mengonfigurasi & Mengunggah Data ke Aiven via Python

Data *time-series* konsentrasi polutan $NO_2$ diunggah secara otomatis dari environment lokal Python menuju cloud database Aiven menggunakan skrip `upload_to_aiven.py`:

```python
import os
import pandas as pd
from sqlalchemy import create_engine

# Path file CSV
csv_path = 'data/processed/data_polutan_no2_clean.csv'
df = pd.read_csv(csv_path)

# Service URI PostgreSQL Aiven
DB_URI = "postgresql://avnadmin:<YOUR_PASSWORD>@pg-3aba66e5-izzulmillahaqil.e.aivencloud.com:21121/defaultdb?sslmode=require"

# Engine & Upload ke Aiven Table
engine = create_engine(DB_URI)
df.to_sql('no2_time_series', con=engine, if_exists='replace', index=False)

print("Data time series berhasil di-upload ke PostgreSQL Aiven!")


## Langkah 3: Menyusun Alur Kerja (Workflow) di KNIME

Beralih menuju **KNIME Analytics Platform** guna menarik data dari cloud database Aiven dan mengekstraksi metrik statistika deskriptif secara otomatis.
```
---

### 3.1 Inisialisasi Workflow Baru
1. Buka aplikasi **KNIME Analytics Platform**.
2. Pada panel **KNIME Explorer** (sebelah kiri), klik kanan pada workspace aktif $\rightarrow$ pilih **New KNIME Workflow**.
3. Beri nama workflow: `PSD_Aiven_KNIME_Pipeline` $\rightarrow$ klik **Finish**.

---

### 3.2 Menambahkan & Menghubungkan Node Repository
Cari node berikut pada panel **Node Repository** (sebelah kiri), lalu *drag-and-drop* ke dalam lembar kerja (*workspace*):

1. **PostgreSQL Connector**  
   * *Fungsi*: Membuka alur koneksi database JDBC dari KNIME ke server cloud Aiven.
2. **DB Table Selector**  
   * *Fungsi*: Memilih skema dan nama tabel spesifik yang tersimpan di dalam database PostgreSQL.
3. **DB Reader**  
   * *Fungsi*: Mengirimkan query SQL dan membaca/memuat isi data tabel dari server cloud ke dalam memori kerja KNIME lokal.
4. **Statistics**  
   * *Fungsi*: Menghitung ringkasan statistik deskriptif (Min, Max, Mean, Median, Std Dev, Skewness, Kurtosis) secara otomatis dari kolom numerik.

#### Alur Hubungan Antar Node (Data Pipeline):
Sambungkan port koneksi (segitiga di tepi node) dari kiri ke kanan dengan urutan:

---

### 3.3 Konfigurasi Parameter Tiap Node

#### A. Node `PostgreSQL Connector`
1. Double-click pada node **PostgreSQL Connector**.
2. Pada tab **Main Properties**, atur parameter berikut:
   * **Hostname**: `pg-3aba66e5-izzulmillahaqil.e.aivencloud.com`
   * **Database name**: `defaultdb`
   * **Port**: `21121`
   * **Authentication**: Pilih `User & Password`
   * **Username**: `avnadmin`
   * **Password**: *(Masukkan password rahasia PostgreSQL Aiven milikmu)*
3. Pilih menu **JDBC Parameters** $\rightarrow$ klik **Set >** / **Add Parameter**:
   * **Property name**: `sslmode`
   * **Value**: `require`
4. Klik **Apply** $\rightarrow$ **Apply and Execute**.  
   *(Indikator di bawah node akan berubah menjadi **HIJAU**)*.

---

#### B. Node `DB Table Selector`
1. Double-click pada node **DB Table Selector**.
2. Pada bagian **Database Outline** / **Schema**:
   * Pilih skema: **`public`**
   * Pilih tabel: **`no2_time_series`**
3. Klik **Apply and Execute**.  
   *(Indikator di bawah node berubah menjadi **HIJAU**)*.

---

#### C. Node `DB Reader`
1. Klik kanan pada node **DB Reader**.
2. Pilih **Execute**.  
   *KNIME akan menarik seluruh baris data $NO_2$ dari Aiven Cloud.*  
   *(Indikator di bawah node berubah menjadi **HIJAU**)*.

---

#### D. Node `Statistics`
1. Double-click pada node **Statistics**.
2. Pada panel konfigurasi sebelah kanan:
   * **Numeric Values**: Pindahkan kolom **`NO2`** ke dalam kotak **Include** (sebelah kanan).
   * **Option Median**: Centang opsi `Calculate median values (computationally expensive)` pada bagian atas untuk menghitung nilai tengah (Median).
3. Klik **Apply and Execute**.