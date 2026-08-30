import openeo
import json
import pandas as pd

connection = openeo.connect("https://openeo.dataspace.copernicus.eu").authenticate_oidc()

with open('geojson/Wilayah.geojson') as f:
    geojson_data = json.load(f)

datacube = connection.load_collection(
    "SENTINEL_5P_L2",
    spatial_extent=geojson_data,
    temporal_extent=["2025-09-01", "2026-08-31"],
    bands=["NO2"]
)

timeseries = datacube.aggregate_spatial(
    geometries=geojson_data,
    reducer="mean"
)

results = timeseries.execute()
df = pd.DataFrame(results)
df.to_csv("data/raw/no2_raw.csv", index=False)