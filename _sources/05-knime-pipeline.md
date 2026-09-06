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