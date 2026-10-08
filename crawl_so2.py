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

# 4. Load Collection openEO untuk SO2
datacube = connection.load_collection(
    "SENTINEL_5P_L2",
    spatial_extent=geojson_data,
    temporal_extent=["2025-09-01", "2026-08-31"],
    bands=["SO2"]
)

# 5. Agregasi Spasial
timeseries = datacube.aggregate_spatial(
    geometries=geojson_data,
    reducer="mean"
)

# 6. Eksekusi dan Transformasi Format ke Vertikal (date, feature_index, SO2)
results = timeseries.execute()

data_list = []
for date_key, values in results.items():
    val = values[0] if (values and values[0] is not None) else None
    formatted_date = date_key.replace('Z', '.000Z') if not date_key.endswith('.000Z') else date_key
    
    data_list.append({
        "date": formatted_date,
        "feature_index": 0,
        "SO2": val
    })

df_raw = pd.DataFrame(data_list)

# 7. Validasi Missing Value di bawah 15%
total_data = len(df_raw)
missing_count = df_raw["SO2"].isna().sum()
missing_pct = (missing_count / total_data) * 100

print(f"[SO2] Total Data: {total_data}, Missing Value: {missing_count} ({missing_pct:.2f}%)")

if missing_pct > 15:
    print("Peringatan: Persentase missing value SO2 di atas 15%!")
else:
    print("Aman: Missing value SO2 di bawah 15%.")

# Imputasi linier & forward/backward fill
df_clean = df_raw.copy()
df_clean["SO2"] = df_clean["SO2"].interpolate(method="time").ffill().bfill()

# Simpan ke folder raw dan processed
df_raw.to_csv("data/raw/so2_raw.csv", index=False)
df_clean.to_csv("data/processed/data_polutan_so2_clean.csv", index=False)

print("Crawling SO2 selesai! Disimpan di data/processed/data_polutan_so2_clean.csv")