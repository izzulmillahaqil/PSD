import os
import zipfile
import uuid
import xml.etree.ElementTree as ET
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

WORKSPACE = r"c:\Users\LENOVO\Documents\SEMESTER 5\PeeSD\PSD"

CLASSES = [
    {
        "class_id": 1,
        "kelas": "Sawah",
        "kode": "sawah",
        "folder": "sawahfix",
        "warna": "#FFD92F",
        "rgb": (255, 217, 47),
    },
    {
        "class_id": 2,
        "kelas": "Bangunan",
        "kode": "bangunan",
        "folder": "Bangunanfix",
        "warna": "#E41A1C",
        "rgb": (228, 26, 28),
    },
    {
        "class_id": 3,
        "kelas": "Mangrove",
        "kode": "mangrove",
        "folder": "mangrovefix",
        "warna": "#8E44AD",
        "rgb": (142, 68, 173),
    },
    {
        "class_id": 4,
        "kelas": "Lahan Hijau",
        "kode": "lahan_hijau",
        "folder": "Lahanhijaufix",
        "warna": "#2E7D32",
        "rgb": (46, 125, 50),
    },
    {
        "class_id": 5,
        "kelas": "Laut",
        "kode": "laut",
        "folder": "lautfix",
        "warna": "#0D47A1",
        "rgb": (13, 71, 161),
    },
    {
        "class_id": 6,
        "kelas": "Danau",
        "kode": "danau",
        "folder": "danau_fix",
        "warna": "#4FC3F7",
        "rgb": (79, 195, 247),
    },
]

SPECTRAL_COLS = [
    "B2_Blue", "B3_Green", "B4_Red", "B8_NIR", "B11_SWIR1", "B12_SWIR2",
    "NDVI", "NDWI", "NDBI", "MNDWI", "SAVI", "BSI"
]

def load_and_merge_data():
    all_records = []
    class_gdfs = {}
    global_id = 1

    # Load spectral reference if exists
    spectral_csv = os.path.join(WORKSPACE, "data", "processed", "dataset_lulc_jatim_300.csv")
    df_spec = None
    if os.path.exists(spectral_csv):
        df_spec = pd.read_csv(spectral_csv)
        print(f"  [*] Memuat data spektral dari {spectral_csv} ({len(df_spec)} baris)")

    print("--- Membaca 6 Folder Shapefile ---")
    for c in CLASSES:
        folder_path = os.path.join(WORKSPACE, c["folder"])
        shp_path = os.path.join(folder_path, "input.shp")
        
        if not os.path.exists(shp_path):
            raise FileNotFoundError(f"File tidak ditemukan: {shp_path}")
            
        gdf = gpd.read_file(shp_path)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        else:
            gdf = gdf.to_crs("EPSG:4326")
            
        # Hitung luas poligon dalam meter persegi & hektar (UTM Zone 49S - Jawa Timur)
        gdf_utm = gdf.to_crs(epsg=32749)
        areas_m2 = gdf_utm.geometry.area.round(2)
        
        # Sub dataset spektral untuk kelas ini
        sub_d = None
        tree = None
        if df_spec is not None:
            sub_d = df_spec[df_spec["Kelas"] == c["kelas"]].reset_index(drop=True)
            if len(sub_d) > 0:
                tree = cKDTree(sub_d[["Latitude", "Longitude"]].values)

        c_records = []
        for i, row in gdf.iterrows():
            orig_id = row.get("@id") or row.get("id") or row.get("FID") or str(i + 1)
            raw_name = row.get("name") or row.get("nama") or row.get("descriptio") or f"{c['kelas']} #{i + 1}"
            centroid = row.geometry.centroid
            lat_c = round(centroid.y, 6)
            lon_c = round(centroid.x, 6)
            luas_val = float(areas_m2.iloc[i])
            luas_ha_val = round(luas_val / 10000.0, 4)

            # Default spectral values
            sample_id = f"{c['kode'][:3].upper()}_{i + 1:02d}"
            spec_vals = {col: 0.0 for col in SPECTRAL_COLS}

            if tree is not None and sub_d is not None and len(sub_d) > 0:
                dist, idx = tree.query([lat_c, lon_c])
                matched_row = sub_d.iloc[idx]
                sample_id = str(matched_row.get("Sample_ID", sample_id))
                for col in SPECTRAL_COLS:
                    spec_vals[col] = round(float(matched_row.get(col, 0.0)), 4)
            
            record = {
                "id": global_id,
                "Sample_ID": sample_id,
                "class_id": c["class_id"],
                "kelas": c["kelas"],
                "kode_kelas": c["kode"],
                "warna": c["warna"],
                "nama": str(raw_name),
                "folder_asal": c["folder"],
                "orig_id": str(orig_id),
                "centroid_x": lon_c,
                "centroid_y": lat_c,
                "luas_m2": luas_val,
                "luas_ha": luas_ha_val,
                **spec_vals,
                "geometry": row.geometry
            }
            all_records.append(record)
            c_records.append(record)
            global_id += 1
            
        class_gdfs[c["kode"]] = gpd.GeoDataFrame(c_records, crs="EPSG:4326")
        print(f"  [OK] {c['kelas']:12} ({c['folder']}): {len(gdf)} poligon")

    merged_gdf = gpd.GeoDataFrame(all_records, crs="EPSG:4326")
    print(f"\nTotal seluruh poligon tergabung: {len(merged_gdf)} fitur")
    return merged_gdf, class_gdfs

def export_geopackage(merged_gdf, class_gdfs, output_gpkg):
    print(f"\n--- Menyimpan ke GeoPackage: {output_gpkg} ---")
    if os.path.exists(output_gpkg):
        os.remove(output_gpkg)
        
    # 1. Simpan layer gabungan (semua kelas)
    merged_gdf.to_file(output_gpkg, layer="semua_kelas", driver="GPKG")
    print(f"  [+] Layer 'semua_kelas' tersimpan ({len(merged_gdf)} poligon)")
    
    # 2. Simpan masing-masing layer kelas agar bisa dipanggil per kelas jika diinginkan
    for kode, gdf in class_gdfs.items():
        gdf.to_file(output_gpkg, layer=kode, driver="GPKG")
        print(f"  [+] Layer '{kode}' tersimpan ({len(gdf)} poligon)")

def export_geojson(merged_gdf, output_geojson):
    print(f"\n--- Menyimpan ke GeoJSON: {output_geojson} ---")
    merged_gdf.to_file(output_geojson, driver="GeoJSON")
    print(f"  [+] GeoJSON tersimpan ({len(merged_gdf)} poligon)")

def create_qgis_project(gpkg_rel_path, output_qgz):
    print(f"\n--- Membuat Proyek QGIS (.qgz): {output_qgz} ---")
    minx, miny, maxx, maxy = 110.89, -9.25, 115.36, -6.45
    
    root = ET.Element("qgis", {
        "projectname": "Tutupan Lahan Jawa Timur (LULC)",
        "version": "3.34.0",
        "saveUser": "LENOVO"
    })
    
    pcrs = ET.SubElement(root, "projectCrs")
    srs = ET.SubElement(pcrs, "spatialrefsys")
    ET.SubElement(srs, "wkt").text = 'GEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north],AXIS["geodetic longitude (Lon)",east],ID["EPSG",4326]]'
    ET.SubElement(srs, "authid").text = "EPSG:4326"
    ET.SubElement(srs, "srid").text = "4326"
    
    ltg = ET.SubElement(root, "layer-tree-group")
    grp = ET.SubElement(ltg, "layer-tree-group", {"name": "Tutupan Lahan (6 Kelas)", "checked": "Qt::Checked", "expanded": "1"})
    
    projectlayers = ET.SubElement(root, "projectlayers")
    layer_order_items = []
    
    # Layer: Semua Kelas
    semua_id = f"semua_kelas_{uuid.uuid4().hex[:8]}"
    ET.SubElement(grp, "layer-tree-layer", {
        "id": semua_id,
        "name": "Semua Kelas LULC (Gabungan 305 Poligon)",
        "checked": "Qt::Checked",
        "expanded": "1",
        "providerKey": "ogr",
        "source": f"{gpkg_rel_path}|layername=semua_kelas"
    })
    layer_order_items.append(semua_id)
    
    ml_semua = ET.SubElement(projectlayers, "maplayer", {
        "type": "vector",
        "wkbType": "MultiPolygon",
        "geometry": "Polygon",
        "hasScaleBasedVisibilityFlag": "0",
        "styleCategories": "AllStyleCategories"
    })
    ET.SubElement(ml_semua, "id").text = semua_id
    ET.SubElement(ml_semua, "datasource").text = f"{gpkg_rel_path}|layername=semua_kelas"
    ET.SubElement(ml_semua, "layername").text = "Semua Kelas LULC (Gabungan 305 Poligon)"
    ET.SubElement(ml_semua, "provider").text = "ogr"
    
    rend = ET.SubElement(ml_semua, "renderer-v2", {
        "type": "categorizedSymbol",
        "attr": "kelas",
        "symbollevels": "0"
    })
    cat_categories = ET.SubElement(rend, "categories")
    cat_symbols = ET.SubElement(rend, "symbols")
    
    for idx, c in enumerate(CLASSES):
        ET.SubElement(cat_categories, "category", {
            "value": c["kelas"],
            "symbol": str(idx),
            "label": f"{c['kelas']} ({c['folder']})",
            "render": "true"
        })
        sym = ET.SubElement(cat_symbols, "symbol", {
            "name": str(idx),
            "type": "fill",
            "alpha": "0.85"
        })
        slayer = ET.SubElement(sym, "layer", {
            "class": "SimpleFill",
            "enabled": "1",
            "locked": "0"
        })
        sopt = ET.SubElement(slayer, "Option", {"type": "Map"})
        r, g, b = c["rgb"]
        ET.SubElement(sopt, "Option", {"name": "color", "type": "QString", "value": f"{r},{g},{b},215"})
        ET.SubElement(sopt, "Option", {"name": "outline_color", "type": "QString", "value": "35,35,35,255"})
        ET.SubElement(sopt, "Option", {"name": "outline_style", "type": "QString", "value": "solid"})
        ET.SubElement(sopt, "Option", {"name": "outline_width", "type": "QString", "value": "0.3"})
        ET.SubElement(sopt, "Option", {"name": "outline_width_unit", "type": "QString", "value": "MM"})
        ET.SubElement(sopt, "Option", {"name": "style", "type": "QString", "value": "solid"})

    # Individual layers
    for c in CLASSES:
        layer_id = f"{c['kode']}_{uuid.uuid4().hex[:8]}"
        ET.SubElement(grp, "layer-tree-layer", {
            "id": layer_id,
            "name": f"{c['kelas']} [{c['folder']}]",
            "checked": "Qt::Unchecked",
            "expanded": "0",
            "providerKey": "ogr",
            "source": f"{gpkg_rel_path}|layername={c['kode']}"
        })
        layer_order_items.append(layer_id)
        
        ml = ET.SubElement(projectlayers, "maplayer", {
            "type": "vector",
            "wkbType": "MultiPolygon",
            "geometry": "Polygon",
            "hasScaleBasedVisibilityFlag": "0",
            "styleCategories": "AllStyleCategories"
        })
        ET.SubElement(ml, "id").text = layer_id
        ET.SubElement(ml, "datasource").text = f"{gpkg_rel_path}|layername={c['kode']}"
        ET.SubElement(ml, "layername").text = f"{c['kelas']} [{c['folder']}]"
        ET.SubElement(ml, "provider").text = "ogr"
        
        rend_single = ET.SubElement(ml, "renderer-v2", {"type": "singleSymbol", "symbollevels": "0"})
        symbols_single = ET.SubElement(rend_single, "symbols")
        sym = ET.SubElement(symbols_single, "symbol", {"name": "0", "type": "fill", "alpha": "0.85"})
        slayer = ET.SubElement(sym, "layer", {"class": "SimpleFill", "enabled": "1", "locked": "0"})
        sopt = ET.SubElement(slayer, "Option", {"type": "Map"})
        r, g, b = c["rgb"]
        ET.SubElement(sopt, "Option", {"name": "color", "type": "QString", "value": f"{r},{g},{b},215"})
        ET.SubElement(sopt, "Option", {"name": "outline_color", "type": "QString", "value": "35,35,35,255"})
        ET.SubElement(sopt, "Option", {"name": "outline_style", "type": "QString", "value": "solid"})
        ET.SubElement(sopt, "Option", {"name": "outline_width", "type": "QString", "value": "0.3"})
        ET.SubElement(sopt, "Option", {"name": "outline_width_unit", "type": "QString", "value": "MM"})
        ET.SubElement(sopt, "Option", {"name": "style", "type": "QString", "value": "solid"})

    mapcanvas = ET.SubElement(root, "mapcanvas")
    ET.SubElement(mapcanvas, "units").text = "degrees"
    extent = ET.SubElement(mapcanvas, "extent")
    ET.SubElement(extent, "xmin").text = str(minx)
    ET.SubElement(extent, "ymin").text = str(miny)
    ET.SubElement(extent, "xmax").text = str(maxx)
    ET.SubElement(extent, "ymax").text = str(maxy)
    
    layerorder = ET.SubElement(root, "layerorder")
    for item in layer_order_items:
        ET.SubElement(layerorder, "item").text = item
        
    xml_data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    
    base_name = os.path.splitext(os.path.basename(output_qgz))[0]
    qgs_filename = f"{base_name}.qgs"
    
    with zipfile.ZipFile(output_qgz, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(qgs_filename, xml_data)
        
    print(f"  [+] File QGIS (.qgz) berhasil dibuat: {output_qgz}")

if __name__ == "__main__":
    merged_gdf, class_gdfs = load_and_merge_data()
    
    gpkg_file = os.path.join(WORKSPACE, "LULC_Jawa_Timur.gpkg")
    geojson_file = os.path.join(WORKSPACE, "LULC_Jawa_Timur.geojson")
    qgz_file = os.path.join(WORKSPACE, "LULC_Jawa_Timur.qgz")
    
    export_geopackage(merged_gdf, class_gdfs, gpkg_file)
    export_geojson(merged_gdf, geojson_file)
    create_qgis_project("LULC_Jawa_Timur.gpkg", qgz_file)
    
    print("\n=== SEMUA PROSES SELESAI DENGAN SUKSES ===")
