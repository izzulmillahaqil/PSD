import os
import ast
import pandas as pd
from sqlalchemy import create_engine

# 1. Cari file CSV
csv_path = 'data/processed/data_polutan_no2_clean.csv'
if not os.path.exists(csv_path):
    csv_path = '../data/processed/data_polutan_no2_clean.csv'

df_raw = pd.read_csv(csv_path)

# 2. Jika formatnya masih 1 baris horizontal, konversi ke 3 kolom vertikal
if len(df_raw) == 1 and len(df_raw.columns) > 10:
    print("Mendeteksi format horizontal lama, mengonversi ke format vertikal...")
    data = []
    for col in df_raw.columns:
        val = df_raw[col].values[0]
        if pd.isna(val) or val in ['[None]', 'None']:
            no2_val = None
        else:
            try:
                parsed = ast.literal_eval(str(val))
                no2_val = parsed[0] if isinstance(parsed, list) else parsed
            except:
                no2_val = None

        date_str = col.replace('Z', '.000Z')
        data.append({'date': date_str, 'feature_index': 0, 'NO2': no2_val})

    df_clean = pd.DataFrame(data)
    # Simpan file CSV yang sudah bersih
    df_clean.to_csv(csv_path, index=False)
else:
    df_clean = df_raw

# 3. Ambil password dari Environment Variable (Aman dari Blokir GitHub)
AIVEN_PASSWORD = os.getenv("AIVEN_PASSWORD")

if not AIVEN_PASSWORD:
    raise ValueError("Error: Variabel environment 'AIVEN_PASSWORD' belum diset di terminal!")

DB_URI = f"postgresql://avnadmin:{AIVEN_PASSWORD}@pg-3aba66e5-izzulmillahaqil.e.aivencloud.com:21121/defaultdb?sslmode=require"
engine = create_engine(DB_URI)

# Timpa tabel lama di Aiven
df_clean.to_sql('no2_time_series', con=engine, if_exists='replace', index=False)

print("SUKSES! Data vertikal dengan kolom 'date', 'feature_index', dan 'NO2' berhasil di-upload ke Aiven!")