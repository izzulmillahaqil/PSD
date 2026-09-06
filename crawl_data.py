import openeo
import json
import pandas as pd
import os

# 1. Buat folder penyimpan jika belum ada
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# 2. Autentikasi openEO
connection = openeo.connect("https://openeo.dataspace.copernicus.eu").authenticate_oidc()

# 3. Read GeoJSON
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

# 6. Eksekusi dan Transformasi Format ke Vertikal (date, feature_index, NO2)
results = timeseries.execute()

data_list = []
for date_key, values in results.items():
    # Ambil nilai NO2 dari list (jika None/kosong diisi None)
    no2_val = values[0] if (values and values[0] is not None) else None
    
    # Format tanggal ISO ke 'YYYY-MM-DDTHH:MM:SS.000Z'
    formatted_date = date_key.replace('Z', '.000Z') if not date_key.endswith('.000Z') else date_key
    
    data_list.append({
        "date": formatted_date,
        "feature_index": 0,
        "NO2": no2_val
    })

# Buat DataFrame vertikal
df_clean = pd.DataFrame(data_list)

# Simpan ke folder raw dan processed
df_clean.to_csv("data/raw/no2_raw.csv", index=False)
df_clean.to_csv("data/processed/data_polutan_no2_clean.csv", index=False)

print("Crawling selesai! Data berhasil disimpan dengan format vertikal di data/processed/data_polutan_no2_clean.csv")