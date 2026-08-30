import openeo
import json
import pandas as pd
import os

# 1. Buat folder penyimpan jika belum ada
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# 2. Autentikasi openEO
connection = openeo.connect("https://openeo.dataspace.copernicus.eu").authenticate_oidc()

# 3. Read GeoJSON (path '../geojson/' karena terminal dijalankan dari folder 'materi')
with open('../geojson/Wilayah.geojson') as f:
    geojson_data = json.load(f)

# 4. Load Collection openEO
datacube = connection.load_collection(
    "SENTINEL_5P_L2",
    spatial_extent=geojson_data,
    temporal_extent=["2025-09-01", "2026-08-31"],
    bands=["NO2"]
)

# 5. Agregasi Spasial
timeseries = datacube.aggregate_spatial(
    geometries=geojson_data,
    reducer="mean"
)

# 6. Eksekusi dan Simpan File
results = timeseries.execute()
df = pd.DataFrame(results)

# Simpan ke folder raw dan processed
df.to_csv("data/raw/no2_raw.csv", index=False)
df.to_csv("data/processed/data_polutan_no2_clean.csv", index=False)

print("Crawling selesai! Data berhasil disimpan di folder data/processed/data_polutan_no2_clean.csv")