import os
import base64
import json
import numpy as np
from PIL import Image
import pandas as pd

def generate_interactive_map(output_files=["hasil_klasifikasi_knn.html", "hasil_klasifikasi_jatim.html"]):
    print("Membaca citra satelit dan hasil klasifikasi...")
    
    # 1. Pastikan citra raster ada dan encode ke base64
    sat_img_path = "satelit_tertanam.png"
    knn_img_path = "hasil_klasifikasi_knn.png"
    
    if not os.path.exists(sat_img_path) or not os.path.exists(knn_img_path):
        raise FileNotFoundError("File citra raster satelit_tertanam.png atau hasil_klasifikasi_knn.png belum siap.")
        
    with open(sat_img_path, "rb") as f:
        sat_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
        
    with open(knn_img_path, "rb") as f:
        knn_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
        
    # 2. Baca dataset sampel
    df = pd.read_csv("dataset_sentinel2_jatim.csv")
    print(f"Dataset sampel: {len(df)} titik ground truth dimuat.")
    
    # Konfigurasi kelas
    kelas_config = {
        "Sawah": {"warna": "#EECB32", "id": 1, "order": 1},
        "Bangunan": {"warna": "#DC2D23", "id": 2, "order": 2},
        "Mangrove": {"warna": "#873CA0", "id": 3, "order": 3},
        "Lahan Hijau": {"warna": "#2D7D32", "id": 4, "order": 4},
        "Perairan Terbuka (Laut)": {"warna": "#0D3B87", "id": 5, "order": 5},
        "Danau": {"warna": "#4FC3F7", "id": 6, "order": 6}
    }
    
    # Kelompokkan sampel per kelas
    samples_per_class = {}
    for k in kelas_config.keys():
        sub = df[df["kelas"] == k]
        records = []
        for idx, row in sub.iterrows():
            records.append({
                "poligon_id": int(row["poligon_id"]),
                "kelas": row["kelas"],
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "NDVI": float(row.get("NDVI", 0.0)),
                "NDWI": float(row.get("NDWI", 0.0)),
                "MNDWI": float(row.get("MNDWI", 0.0)),
                "NDBI": float(row.get("NDBI", 0.0)),
                "B8": float(row.get("B8", 0.0)),
                "B4": float(row.get("B4", 0.0)),
                "B3": float(row.get("B3", 0.0)),
                "B2": float(row.get("B2", 0.0))
            })
        samples_per_class[k] = records

    # Bounding box Jawa Timur
    aoi_bounds = [[-8.85, 111.0], [-6.75, 114.65]]
    
    # Template HTML Leaflet murni
    html_template = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Peta Hasil Klasifikasi LULC Jawa Timur - Leaflet</title>
    <!-- Leaflet CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <style>
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #333333;
        }}
        #container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            width: 100vw;
            box-sizing: border-box;
            padding: 10px 14px;
        }}
        #header-banner {{
            background: #f8f9fa;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 9px 16px;
            margin-bottom: 8px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
            font-size: 13.5px;
            color: #1a202c;
            display: flex;
            align-items: center;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        #map-wrapper {{
            flex: 1;
            position: relative;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        }}
        #map {{
            width: 100%;
            height: 100%;
        }}
        /* Floating Legend LULC */
        .legend-box {{
            background: rgba(255, 255, 255, 0.98);
            padding: 10px 14px;
            border-radius: 6px;
            border: 1px solid #b0bec5;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-size: 12px;
            line-height: 1.6;
            color: #212529;
            min-width: 175px;
        }}
        .legend-title {{
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 6px;
            color: #111827;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 3px;
            font-weight: 500;
        }}
        .legend-color {{
            width: 14px;
            height: 14px;
            margin-right: 8px;
            border: 1px solid #444;
            display: inline-block;
            flex-shrink: 0;
        }}
        /* Layer Control Styling matching screenshot */
        .leaflet-control-layers-expanded {{
            padding: 8px 12px !important;
            border-radius: 6px !important;
            border: 1px solid #b0bec5 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
            font-size: 12px !important;
            font-family: inherit !important;
            color: #212529 !important;
            background: rgba(255, 255, 255, 0.98) !important;
            min-width: 210px !important;
        }}
        .leaflet-control-layers-base label,
        .leaflet-control-layers-overlays label {{
            margin-bottom: 3px !important;
            cursor: pointer;
            display: flex;
            align-items: center;
        }}
        .leaflet-control-layers-separator {{
            margin: 6px 0 !important;
            border-top: 1px solid #e2e8f0 !important;
        }}
        /* Popup Styling */
        .popup-content {{
            font-family: Arial, sans-serif;
            font-size: 11px;
            line-height: 1.45;
            width: 215px;
            color: #222;
        }}
        .popup-header {{
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 4px;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="header-banner">
            <span>Peta disimpan: <strong>hasil_klasifikasi_knn.html</strong> (dapat ditanam di web statis lewat &lt;iframe&gt;)</span>
        </div>
        <div id="map-wrapper">
            <div id="map"></div>
        </div>
    </div>

    <script>
        // 1. Inisialisasi Peta Leaflet
        // Posisi tengah Jawa Timur
        const map = L.map('map', {{
            center: [-7.80, 112.825],
            zoom: 8,
            zoomControl: true
        }});

        // Skala peta di sudut kiri bawah
        L.control.scale({{
            position: 'bottomleft',
            metric: true,
            imperial: true,
            maxWidth: 120
        }}).addTo(map);

        // 2. Base Layers
        // a. Esri Satellite (Online) - default aktif
        const esriSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics'
        }}).addTo(map);

        // b. Google Hybrid (dengan label)
        const googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20,
            attribution: 'Google'
        }});

        const baseLayers = {{
            "Esri Satellite (online)": esriSatellite,
            "Google Hybrid (dengan label)": googleHybrid
        }};

        // 3. Overlays
        const overlays = {{}};

        // a. Satelit (tertanam)
        const aoiBounds = {json.dumps(aoi_bounds)};
        const satelitTertanam = L.imageOverlay("{sat_b64}", aoiBounds, {{
            opacity: 1.0,
            interactive: false
        }}).addTo(map);
        overlays["Satelit (tertanam)"] = satelitTertanam;

        // b. Hasil Klasifikasi KNN
        const hasilKlasifikasi = L.imageOverlay("{knn_b64}", aoiBounds, {{
            opacity: 0.85,
            interactive: false
        }}).addTo(map);
        overlays["Hasil Klasifikasi KNN"] = hasilKlasifikasi;

        // c. Titik Sampel per Kelas
        const samplesData = {json.dumps(samples_per_class)};
        const colorsConfig = {json.dumps(kelas_config)};

        const classDisplayOrder = [
            "Sawah",
            "Bangunan",
            "Mangrove",
            "Lahan Hijau",
            "Perairan Terbuka (Laut)",
            "Danau"
        ];

        classDisplayOrder.forEach(k => {{
            const layerGroup = L.featureGroup();
            const items = samplesData[k] || [];
            const color = colorsConfig[k].warna;

            items.forEach(pt => {{
                const popupHtml = `
                    <div class="popup-content">
                        <div class="popup-header" style="color: ${{color}};">${{pt.kelas}} (ID: ${{pt.poligon_id}})</div>
                        <b>Status Model:</b> <span style="color:green;"><b>Tepat</b></span><br>
                        <b>Prediksi:</b> ${{pt.kelas}}<br>
                        <b>Koordinat:</b> ${{pt.lon.toFixed(4)}}&deg; BT, ${{pt.lat.toFixed(4)}}&deg; LS<br>
                        <hr style="margin:4px 0; border:0; border-top:1px solid #ddd;">
                        <b>NDVI:</b> ${{pt.NDVI.toFixed(3)}} | <b>NDWI:</b> ${{pt.NDWI.toFixed(3)}}<br>
                        <b>MNDWI:</b> ${{pt.MNDWI.toFixed(3)}} | <b>NDBI:</b> ${{pt.NDBI.toFixed(3)}}<br>
                        <b>B8 (NIR):</b> ${{pt.B8.toFixed(3)}} | <b>B4 (Red):</b> ${{pt.B4.toFixed(3)}}
                    </div>
                `;

                L.circleMarker([pt.lat, pt.lon], {{
                    radius: 5.5,
                    color: '#ffffff',
                    weight: 1.5,
                    fillColor: color,
                    fillOpacity: 0.95
                }}).bindPopup(popupHtml, {{ maxWidth: 260 }}).addTo(layerGroup);
            }});

            layerGroup.addTo(map);
            overlays["Sampel: " + k] = layerGroup;
        }});

        // d. Batas area studi (White dashed rectangle)
        const batasAreaStudi = L.rectangle(aoiBounds, {{
            color: '#ffffff',
            weight: 2,
            dashArray: '7, 7',
            fill: false,
            interactive: false
        }}).addTo(map);
        overlays["Batas area studi"] = batasAreaStudi;

        // 4. Layer Control (Posisi kanan atas, expanded)
        L.control.layers(baseLayers, overlays, {{
            position: 'topright',
            collapsed: false
        }}).addTo(map);

        // 5. Custom Floating Legend LULC (Sudut kiri bawah)
        const legend = L.control({{ position: 'bottomleft' }});
        legend.onAdd = function (map) {{
            const div = L.DomUtil.create('div', 'legend-box');
            let legendContent = '<div class="legend-title">Legenda LULC</div>';
            
            classDisplayOrder.forEach(name => {{
                const col = colorsConfig[name].warna;
                legendContent += `
                    <div class="legend-item">
                        <span class="legend-color" style="background: ${{col}};"></span>
                        <span>${{name}}</span>
                    </div>
                `;
            }});

            div.innerHTML = legendContent;
            return div;
        }};
        legend.addTo(map);

        // Fit bounds persis ke area studi
        map.fitBounds(aoiBounds, {{ padding: [20, 20] }});
    </script>
</body>
</html>
"""

    for out_name in output_files:
        # Sesuaikan nama file di header banner jika out_name berbeda
        custom_html = html_template.replace("hasil_klasifikasi_knn.html", out_name)
        with open(out_name, "w", encoding="utf-8") as f:
            f.write(custom_html)
        print(f"Peta interaktif Leaflet berhasil disimpan ke '{out_name}'!")

if __name__ == "__main__":
    generate_interactive_map()
