'''generate_dataset_from_shp.py
Generate a CSV dataset that combines class labels (from the provided shapefiles) with
Sentinel‑2 spectral band values sampled at the centroid of each polygon.

The script follows the same logic as the notebook `klasifikasi_lulc_decision_tree.ipynb`
but is fully automated so you can run it once to create the required
`dataset_sentinel2_jatim.csv`.

Usage (from the project root):
    python generate_dataset_from_shp.py

Make sure you have the required Python packages installed:
    pip install geopandas rasterio pandas tqdm

You may need to adjust the paths in the sections marked "# >>> USER SETTINGS <<<".
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
# Directory where the class shapefiles live (the same structure used in the notebook)
DATA_DIR = os.path.abspath('.')  # project root

# Mapping of class IDs to their metadata – copy‑paste from the notebook for consistency
KELAS = {
    1: dict(nama="Sawah",                   file="sawahfix",       n=50, warna="#FFD92F"),
    2: dict(nama="Bangunan",                file="Bangunanfix",    n=50, warna="#E41A1C"),
    3: dict(nama="Mangrove",                file="mangrovefix",    n=50, warna="#8E44AD"),
    4: dict(nama="Lahan Hijau",             file="Lahanhijaufix",  n=50, warna="#2E7D32"),
    5: dict(nama="Perairan Terbuka (Laut)", file="lautfix",        n=35, warna="#0D47A1"),
    6: dict(nama="Danau",                   file="danau_fix",      n=50, warna="#4FC3F7"),
}

# Sentinel‑2 band identifiers – the notebook expects 10 original bands + 8 indices
BAND_ASLI = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
INDIKS = ["NDVI", "NDWI", "MNDWI", "NDBI", "NDRE", "EVI", "SAVI", "BSI"]
FITUR_SEMUA = BAND_ASLI + INDIKS

# Folder that contains the raster files. The script expects one GeoTIFF per band
# named exactly like "B2.tif", "B3.tif", … (you can rename them or change the mapping below).
RASTER_DIR = os.path.join(DATA_DIR, "sentinel2_bands")

# Output CSV filename (the same name that the notebook looks for)
CSV_DATASET = "dataset_sentinel2_jatim.csv"
# ------------------------------------------------------------
# End of user‑editable section
# ------------------------------------------------------------

warnings.filterwarnings('ignore')

def load_band(band_name: str):
    """Load a single band raster and return the opened dataset.
    The file must be named `<band_name>.tif` inside ``RASTER_DIR``.
    """
    path = os.path.join(RASTER_DIR, f"{band_name}.tif")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Band file not found: {path}")
    return rasterio.open(path)

def sample_point(raster, point):
    """Return the raster value at *point* (shapely geometry).
    The point is transformed automatically to the raster CRS if needed.
    """
    if raster.crs != point.crs:
        # re‑project point on‑the‑fly
        transformer = rasterio.warp.transformer.Transformer.from_crs(point.crs, raster.crs, always_xy=True)
        xs, ys = transformer.transform(point.x, point.y)
    else:
        xs, ys = point.x, point.y
    return list(raster.sample([(xs, ys)]))[0][0]

def main():
    # -----------------------------------------------------------------
    # Load all raster bands once – this avoids opening/closing files for every point.
    # -----------------------------------------------------------------
    print("Loading raster bands …")
    band_datasets = {b: load_band(b) for b in BAND_ASLI}

    # -----------------------------------------------------------------
    # Prepare a list to collect rows for the final DataFrame.
    # -----------------------------------------------------------------
    rows = []
    global_id = 0

    for class_id, meta in tqdm(KELAS.items(), desc="Classes"):
        shp_path = os.path.join(DATA_DIR, meta["file"], "input.shp")
        if not os.path.exists(shp_path):
            raise FileNotFoundError(f"Shapefile not found for class {class_id}: {shp_path}")
        gdf = gpd.read_file(shp_path)
        gdf = gdf.set_crs(4326) if gdf.crs is None else gdf.to_crs(4326)
        # Use only the geometry column – the notebook only needs the centroid.
        for idx, row in gdf.iterrows():
            centroid = row.geometry.centroid
            # Sample each band at the centroid
            band_values = {}
            for b_name, ds in band_datasets.items():
                try:
                    val = ds.read(1, window=rasterio.windows.Window(0, 0, ds.width, ds.height),
                                   boundless=True, resampling=Resampling.bilinear)
                    # Faster: use sample() for a single point
                    val = list(ds.sample([(centroid.x, centroid.y)]))[0][0]
                except Exception as e:
                    val = np.nan
                band_values[b_name] = float(val) if val is not None else np.nan
            # Build the row dictionary
            row_dict = {
                "id": global_id,
                "kelas": meta["nama"],
                "wilayah": meta["file"],
            }
            row_dict.update(band_values)
            rows.append(row_dict)
            global_id += 1
    # -----------------------------------------------------------------
    # Create DataFrame and write CSV
    # -----------------------------------------------------------------
    df = pd.DataFrame(rows)
    # Re‑order columns to match the notebook expectations (class columns first)
    cols_order = [c for c in df.columns if c not in FITUR_SEMUA]
    cols_order += FITUR_SEMUA
    df = df[cols_order]
    output_path = os.path.join(DATA_DIR, CSV_DATASET)
    df.to_csv(output_path, index=False)
    print(f"\n✅ Dataset written to {output_path}")
    print(f"   Rows   : {df.shape[0]}")
    print(f"   Columns: {df.shape[1]} (including {len(FITUR_SEMUA)} spectral features)")

if __name__ == "__main__":
    main()
'''
