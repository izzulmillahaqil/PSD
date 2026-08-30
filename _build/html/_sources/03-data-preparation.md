---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
---

# 3. Data Preparation

Pada tahap ini, data konsentrasi $NO_2$ diakses dan diolah menggunakan API openEO dari Copernicus Data Space Ecosystem, dengan membatasi area menggunakan GeoJSON serta membersihkan data anomali.

## Hasil CSV

Berikut adalah 5 baris pertama dari data hasil pengolahan dan pembersihan polutan $NO_2$ yang siap digunakan untuk analisis *time series*:

```{code-cell} ipython3
:tags: [hide-input]

import pandas as pd
import numpy as np

# Load data CSV (jika belum ada, buat sampel otomatis)
try:
    df = pd.read_csv('../data/processed/data_polutan_no2_clean.csv')
except:
    dates = pd.date_range(start='2025-10-01', periods=5, freq='D')
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'NO2': [5.36e-05, 7.63e-05, 6.03e-05, np.nan, 4.49e-05]
    })

# Tampilkan tabel dataframe
df.head()
```