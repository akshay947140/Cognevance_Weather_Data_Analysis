"""
generate_dataset.py
--------------------
Generates a realistic 2-year daily weather dataset for a mid-latitude city,
complete with seasonal temperature/humidity/rainfall patterns AND common
real-world data quality problems (missing values, duplicate rows, impossible
readings, inconsistent text casing). This mimics what you'd typically find
after downloading a raw dataset from Kaggle, so the cleaning step in
clean_analyze.py has real work to do.

Run: python3 generate_dataset.py
Output: ../data/weather_raw.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

START_DATE = datetime(2023, 1, 1)
NUM_DAYS = 730  # 2 years

dates = [START_DATE + timedelta(days=i) for i in range(NUM_DAYS)]

records = []
for d in dates:
    day_of_year = d.timetuple().tm_yday

    # Seasonal temperature curve (Northern Hemisphere, peak in July)
    seasonal_temp = 18 + 12 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    temp = seasonal_temp + np.random.normal(0, 3)

    # Humidity inversely related to temp, with noise
    humidity = 70 - 0.6 * (temp - 18) + np.random.normal(0, 8)
    humidity = np.clip(humidity, 20, 100)

    # Rainfall: more likely in cooler / humid periods, mostly zero
    rain_chance = 0.25 + 0.15 * (humidity - 50) / 50
    rainfall = 0.0
    if np.random.random() < max(rain_chance, 0.05):
        rainfall = np.random.exponential(scale=8)

    # Month name (sometimes inconsistent casing to simulate messy data)
    month_name = d.strftime("%B")
    if np.random.random() < 0.05:
        month_name = month_name.lower()

    records.append({
        "date": d.strftime("%Y-%m-%d"),
        "month": month_name,
        "temperature_C": round(temp, 1),
        "humidity_pct": round(humidity, 1),
        "rainfall_mm": round(rainfall, 1),
    })

df = pd.DataFrame(records)

# ---- Inject realistic data quality problems ----

# 1. Missing values (~4% of temperature, ~3% of humidity, ~2% of rainfall)
for col, frac in [("temperature_C", 0.04), ("humidity_pct", 0.03), ("rainfall_mm", 0.02)]:
    idx = df.sample(frac=frac, random_state=1).index
    df.loc[idx, col] = np.nan

# 2. Impossible / erroneous readings (sensor glitches)
glitch_idx = df.sample(n=8, random_state=2).index
df.loc[glitch_idx[:3], "temperature_C"] = 999.0        # obviously bad sensor value
df.loc[glitch_idx[3:5], "humidity_pct"] = -15.0         # negative humidity, impossible
df.loc[glitch_idx[5:8], "rainfall_mm"] = -5.0           # negative rainfall, impossible

# 3. Duplicate rows
dupes = df.sample(n=10, random_state=3)
df = pd.concat([df, dupes], ignore_index=True)

# 4. Shuffle so duplicates aren't neatly at the end (more realistic)
df = df.sample(frac=1, random_state=4).reset_index(drop=True)

df.to_csv("/home/claude/weather_project/data/weather_raw.csv", index=False)
print(f"Generated {len(df)} rows -> data/weather_raw.csv")
print(df.head())
