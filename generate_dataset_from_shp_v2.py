'''generate_dataset_from_shp_v2.py
Generate a CSV dataset that combines class labels (from the provided shapefiles) with
Sentinel‑2 spectral band values sampled at each polygon centroid.

The script follows the same logic as the notebook `klasifikasi_lulc_decision_tree.ipynb`
but is fully automated so you can run it once to create the required
`dataset_sentinel2_jatim.csv`.

Usage (from the project root)::
    python generate_dataset_from_shp_v2.py

Make sure you have the required Python packages installed::
    pip install geopandas rasterio pandas tqdm

Place the Sentinel‑2 GeoTIFF raster files (one file per band, named like ``B2.tif``) in the
folder ``sentinel2_bands`` at the project root. If a band file is missing the script will
store ``NaN`` for that band.
''' 

import os
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.enums import Resampling
from tqdm import tqdm

# ------------------------------------------------------------
# >>> USER SETTINGS <<<
# ------------------------------------------------------------
PROJECT_ROOT = os.path.abspath('.')

KELAS = {
    1: dict(nama="Sawah",               file="sawahfix",       n=50, warna="#FFD92F"),
    2: dict(nama="Bangunan",            file="Bangunanfix",    n=50, warna="#E41A1C"),
    3: dict(nama="Mangrove",            file="mangrovefix",    n=50, warna="#8E44AD"),
    4: dict(nama="Lahan Hijau",         file="Lahanhijaufix",  n=50, warna="#2E7D32"),
    5: dict(nama="Perairan Terbuka (Laut)", file="lautfix",        n=35, warna="#0D47A1"),
    6: dict(nama="Danau",               file="danau_fix",      n=50, warna="#4FC3F7"),
}

BAND_ASLI = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
INDIKS = ["NDVI", "NDWI", "MNDWI", "NDBI", "NDRE", "EVI", "SAVI", "BSI"]
FITUR_SEMUA = BAND_ASLI

RASTER_DIR = os.path.join(PROJECT_ROOT, "sentinel2_bands")
CSV_DATASET = "dataset_sentinel2_jatim.csv"
# ------------------------------------------------------------
# End of user‑editable section
# ------------------------------------------------------------

warnings.filterwarnings('ignore')

def load_band(band_name: str):
    """Load a single band raster and return the opened dataset.
    Returns None if the file is missing.
    """
    path = os.path.join(RASTER_DIR, f"{band_name}.tif")
    if not os.path.exists(path):
        return None
    return rasterio.open(path)

def sample_at_point(raster, point):
    """Return the raster value at *point* (shapely geometry). Handles CRS mismatch.
    Returns NaN if raster is None or sampling fails.
    """
    if raster is None:
        return np.nan
    if raster.crs != point.crs:
        transformer = rasterio.warp.transformer.Transformer.from_crs(point.crs, raster.crs, always_xy=True)
        xs, ys = transformer.transform(point.x, point.y)
    else:
        xs, ys = point.x, point.y
    try:
        val = list(raster.sample([(xs, ys)]))[0][0]
        return float(val) if val is not None else np.nan
    except Exception:
        return np.nan

def main():
    print("Loading raster bands ...")
    band_datasets = {b: load_band(b) for b in BAND_ASLI}

    rows = []
    gid = 0
    for class_id, meta in tqdm(KELAS.items(), desc="Classes"):
        shp_path = os.path.join(PROJECT_ROOT, meta["file"], "input.shp")
        if not os.path.exists(shp_path):
            raise FileNotFoundError(f"Shapefile not found for class {class_id}: {shp_path}")
        gdf = gpd.read_file(shp_path)
        gdf = gdf.set_crs(4326) if gdf.crs is None else gdf.to_crs(4326)
        for _, row in gdf.iterrows():
            centroid = row.geometry.centroid
            band_values = {b: sample_at_point(ds, centroid) for b, ds in band_datasets.items()}
            row_dict = {"id": gid, "kelas": meta["nama"], "wilayah": meta["file"]}
            row_dict.update(band_values)
            rows.append(row_dict)
            gid += 1
    df = pd.DataFrame(rows)
    cols_order = [c for c in df.columns if c not in FITUR_SEMUA]
    cols_order += FITUR_SEMUA
    df = df[cols_order]
    out_path = os.path.join(PROJECT_ROOT, CSV_DATASET)
    df.to_csv(out_path, index=False)
    print(f"\nDataset written to {out_path}")
    print(f"   Rows   : {df.shape[0]}")
    print(f"   Columns: {df.shape[1]} (including {len(FITUR_SEMUA)} spectral features)")

if __name__ == "__main__":
    main()
