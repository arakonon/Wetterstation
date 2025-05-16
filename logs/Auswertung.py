import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


csv_file = Path("~/Wetterstation/logs/innen.csv").expanduser()
df = pd.read_csv(csv_file, parse_dates=["timestamp"])

df = df.set_index("timestamp")

df[["temp_c", "hum_rel", "co2_ppm"]].plot(figsize=(10, 5))
plt.xlabel("Zeit")
plt.ylabel("Messwert")
plt.title("Innenstation – Temperatur, rel. Feuchte, CO₂")
plt.tight_layout()
plt.show()