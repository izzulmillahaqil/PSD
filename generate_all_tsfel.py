import os
import pandas as pd

# 1. Cari lokasi folder file skrip ini berada
base_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Tentukan target output folder secara pasti
output_dir = os.path.join(base_dir, "data", "processed")
os.makedirs(output_dir, exist_ok=True)

# 3. Daftar file TSFEL masing-masing polutan
files = {
    "SO2": "SO2_Surabaya_Selatan_TSFEL.csv",
    "NO2": "NO2_Surabaya_Selatan_TSFEL.csv",
    "CO": "CO_Surabaya_Selatan_TSFEL.csv",
}

dfs = []

# 4. Baca file dari folder lokal atau data/processed
for pol, filename in files.items():
  file_path = os.path.join(base_dir, filename)
  if not os.path.exists(file_path):
    file_path = os.path.join(output_dir, filename)

  print(f"Membaca {pol} dari: {file_path}")
  df = pd.read_csv(file_path)

  # Beri prefix nama polutan pada tiap kolom
  renamed_cols = {}
  for col in df.columns:
    if not col.startswith(f"{pol}_"):
      renamed_cols[col] = f"{pol}_{col}"
    else:
      renamed_cols[col] = col

  df = df.rename(columns=renamed_cols)
  dfs.append(df)

# 5. Gabungkan ketiga DataFrame secara horizontal (204 kolom)
df_final_204 = pd.concat(dfs, axis=1)

# 6. Simpan secara presisi ke folder data/processed
output_path = os.path.join(output_dir, "Semua_Polutan_204_Fitur_TSFEL.csv")
df_final_204.to_csv(output_path, index=False)

print("\n==========================================")
print("PROSES SELESAI!")
print(f"Total Kolom Berhasil Digabung: {df_final_204.shape[1]}")
print(f"File BERHASIL tersimpan di: {output_path}")
print("==========================================")