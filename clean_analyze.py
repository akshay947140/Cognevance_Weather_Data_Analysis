"""
clean_analyze.py
-----------------
Loads the raw weather dataset, cleans it (missing values, impossible
readings, duplicates, inconsistent text), then analyzes temperature,
humidity, and rainfall trends across months and seasons, producing
charts and a cleaned CSV.

Run: python3 clean_analyze.py
Inputs:  ../data/weather_raw.csv
Outputs: ../data/weather_clean.csv
         ../data/monthly_summary.csv
         ../charts/*.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

DATA_DIR = "/home/claude/weather_project/data"
CHART_DIR = "/home/claude/weather_project/charts"

# ---------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------
df = pd.read_csv(f"{DATA_DIR}/weather_raw.csv", parse_dates=["date"])
print(f"Raw rows loaded: {len(df)}")

# ---------------------------------------------------------------
# 2. CLEAN
# ---------------------------------------------------------------

# 2a. Remove exact duplicate rows
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows")

# 2b. Normalize month text casing
df["month"] = df["month"].str.capitalize()

# 2c. Flag and null-out physically impossible readings
# Realistic bounds for a mid-latitude climate:
#   temperature: -30C to 50C | humidity: 0-100% | rainfall: >= 0mm
bad_temp = ~df["temperature_C"].between(-30, 50)
bad_hum = ~df["humidity_pct"].between(0, 100)
bad_rain = df["rainfall_mm"] < 0

print(f"Invalid temperature readings: {bad_temp.sum()}")
print(f"Invalid humidity readings: {bad_hum.sum()}")
print(f"Invalid rainfall readings: {bad_rain.sum()}")

df.loc[bad_temp, "temperature_C"] = np.nan
df.loc[bad_hum, "humidity_pct"] = np.nan
df.loc[bad_rain, "rainfall_mm"] = np.nan

# 2d. Handle missing values
# Temperature & humidity: interpolate along the date axis (smooth, continuous
# physical quantities) after sorting chronologically.
# Rainfall: missing usually means "not recorded" for a mostly-dry day in this
# synthetic set, but safer practice is to impute with the monthly median
# rather than assume zero.
df = df.sort_values("date").reset_index(drop=True)

missing_before = df[["temperature_C", "humidity_pct", "rainfall_mm"]].isna().sum()

df["temperature_C"] = df["temperature_C"].interpolate(method="linear", limit_direction="both")
df["humidity_pct"] = df["humidity_pct"].interpolate(method="linear", limit_direction="both")
df["rainfall_mm"] = df.groupby("month")["rainfall_mm"].transform(
    lambda s: s.fillna(s.median())
)

missing_after = df[["temperature_C", "humidity_pct", "rainfall_mm"]].isna().sum()
print("\nMissing values before -> after cleaning:")
for col in ["temperature_C", "humidity_pct", "rainfall_mm"]:
    print(f"  {col}: {missing_before[col]} -> {missing_after[col]}")

# 2e. Derived columns
df["year"] = df["date"].dt.year
df["month_num"] = df["date"].dt.month
season_map = {12: "Winter", 1: "Winter", 2: "Winter",
              3: "Spring", 4: "Spring", 5: "Spring",
              6: "Summer", 7: "Summer", 8: "Summer",
              9: "Autumn", 10: "Autumn", 11: "Autumn"}
df["season"] = df["month_num"].map(season_map)

df.to_csv(f"{DATA_DIR}/weather_clean.csv", index=False)
print(f"\nCleaned dataset saved: {len(df)} rows -> data/weather_clean.csv")

# ---------------------------------------------------------------
# 3. MONTHLY / SEASONAL ANALYSIS
# ---------------------------------------------------------------
month_order = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]

monthly = df.groupby("month").agg(
    avg_temp_C=("temperature_C", "mean"),
    avg_humidity_pct=("humidity_pct", "mean"),
    total_rainfall_mm=("rainfall_mm", "sum"),
    avg_rainfall_mm=("rainfall_mm", "mean"),
).reindex(month_order)
monthly = monthly.round(2)
monthly.to_csv(f"{DATA_DIR}/monthly_summary.csv")
print("\nMonthly summary:\n", monthly)

seasonal = df.groupby("season").agg(
    avg_temp_C=("temperature_C", "mean"),
    avg_humidity_pct=("humidity_pct", "mean"),
    total_rainfall_mm=("rainfall_mm", "sum"),
).round(2)
print("\nSeasonal summary:\n", seasonal)

# ---------------------------------------------------------------
# 4. CHARTS
# ---------------------------------------------------------------

# 4a. Monthly average temperature (line)
plt.figure(figsize=(10, 5))
plt.plot(monthly.index, monthly["avg_temp_C"], marker="o", color="#d62728")
plt.title("Average Monthly Temperature")
plt.ylabel("Temperature (°C)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/01_monthly_avg_temperature.png")
plt.close()

# 4b. Monthly average humidity (line)
plt.figure(figsize=(10, 5))
plt.plot(monthly.index, monthly["avg_humidity_pct"], marker="o", color="#1f77b4")
plt.title("Average Monthly Humidity")
plt.ylabel("Humidity (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/02_monthly_avg_humidity.png")
plt.close()

# 4c. Total monthly rainfall (bar)
plt.figure(figsize=(10, 5))
sns.barplot(x=monthly.index, y=monthly["total_rainfall_mm"], color="#2ca02c")
plt.title("Total Monthly Rainfall")
plt.ylabel("Rainfall (mm)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/03_monthly_total_rainfall.png")
plt.close()

# 4d. Temperature distribution by season (boxplot)
plt.figure(figsize=(8, 5))
season_order = ["Winter", "Spring", "Summer", "Autumn"]
sns.boxplot(data=df, x="season", y="temperature_C", order=season_order, palette="coolwarm")
plt.title("Temperature Distribution by Season")
plt.ylabel("Temperature (°C)")
plt.xlabel("")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/04_seasonal_temperature_boxplot.png")
plt.close()

# 4e. Temperature vs Humidity scatter (relationship)
plt.figure(figsize=(7, 6))
sns.scatterplot(data=df, x="temperature_C", y="humidity_pct", hue="season",
                 hue_order=season_order, alpha=0.6, s=25)
plt.title("Temperature vs Humidity")
plt.xlabel("Temperature (°C)")
plt.ylabel("Humidity (%)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/05_temp_vs_humidity_scatter.png")
plt.close()

# 4f. Correlation heatmap
plt.figure(figsize=(5, 4))
corr = df[["temperature_C", "humidity_pct", "rainfall_mm"]].corr()
sns.heatmap(corr, annot=True, cmap="vlag", fmt=".2f", vmin=-1, vmax=1)
plt.title("Correlation Between Variables")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/06_correlation_heatmap.png")
plt.close()

print(f"\n6 charts saved to {CHART_DIR}/")
