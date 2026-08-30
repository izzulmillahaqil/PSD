# 3. Data Preparation

Pada tahap ini, data konsentrasi $NO_2$ diakses dan diolah menggunakan API **openEO** dari Copernicus Data Space Ecosystem, dengan membatasi area menggunakan GeoJSON serta membersihkan data anomali.

## Akses Data via openEO Python Client

Proses ekstraksi data dilakukan secara otomatis dengan mendefinisikan *bounding box* dari file `Wilayah.geojson` dan memuat koleksi Sentinel-5P L2.

```python
import openeo
import json
import pandas as pd

# 1. Koneksi ke Copernicus Data Space Ecosystem
connection = openeo.connect("https://openeo.dataspace.copernicus.eu").authenticate_oidc()

# 2. Muat area observasi dari GeoJSON
with open('geojson/Wilayah.geojson') as f:
    geojson_data = json.load(f)

# 3. Buat datacube openEO untuk Sentinel-5P NO2
datacube = connection.load_collection(
    "SENTINEL_5P_L2",
    spatial_extent=geojson_data,
    temporal_extent=["2025-09-01", "2026-08-31"],
    bands=["NO2"]
)

# 4. Agregasi spasial (rata-rata nilai NO2 di dalam polygon area)
timeseries = datacube.aggregate_spatial(
    geometries=geojson_data,
    reducer="mean"
)

# 5. Eksekusi job dan simpan hasil ke CSV
results = timeseries.execute()
```

## Cleaning & Interpolasi Data

Data hasil ekstraksi satelit kerap memiliki *gap* akibat tutupan awan (*cloud cover*). Pembersihan dilakukan dengan pandas:

```python
# Membaca data mentah dan menangani missing values
df = pd.read_csv('data/raw/no2_raw.csv')
df['date'] = pd.to_datetime(df['date'])

# Hapus nilai outlier negatif/anomali sensor
df['NO2'] = df['NO2'].apply(lambda x: None if x < 0 else x)

# Interpolasi linier untuk mengisi tanggal yang kosong akibat awan
df['NO2_clean'] = df['NO2'].interpolate(method='linear')

# Simpan ke folder processed
df.to_csv('data/processed/data_polutan_no2_clean.csv', index=False)
```