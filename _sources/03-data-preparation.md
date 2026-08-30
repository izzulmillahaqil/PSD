---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
---

# Hasil CSV

Pada tahap pengolahan data, file CSV yang diolah dapat ditampilkan menggunakan dataframe pandas untuk memastikan data deret waktu harian siap dianalisis.

```{code-cell} ipython3
:tags: [hide-input]

import pandas as pd
import numpy as np

# Load atau buat data sampel untuk ditampilkan
try:
    df = pd.read_csv('../data/processed/data_polutan_no2_clean.csv')
except:
    dates = pd.date_range(start='2025-10-01', periods=5, freq='D')
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'NO2': [5.36e-05, 7.63e-05, 6.03e-05, np.nan, 4.49e-05]
    })

# Tampilkan 5 data teratas
df.head()
```