import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime  

df = pd.read_csv("innen.csv", parse_dates=["timestamp"]).set_index("timestamp")

fig, axes = plt.subplots(9, 1, sharex=True, figsize=(10, 18))

df["temp_c"].plot(ax=axes[0], legend=False, color="tab:red")
axes[0].set_ylabel("Innen °C")

df["temp_out"].plot(ax=axes[1], legend=False, color="tab:orange")
axes[1].set_ylabel("Außen °C")

df["hum_rel"].plot(ax=axes[2], legend=False, color="tab:blue")
axes[2].set_ylabel("Innen % rF")

df["hum_out"].plot(ax=axes[3], legend=False, color="tab:green")
axes[3].set_ylabel("Außen % rF")

df["co2_ppm"].plot(ax=axes[4], legend=False, color="tab:gray")
axes[4].set_ylabel("CO₂ ppm")

df["iaq"].plot(ax=axes[5], legend=False, color="tab:brown")
axes[5].set_ylabel("IAQ")

df["uv_kategorie"].plot(ax=axes[6], legend=False, color="tab:pink")
axes[6].set_ylabel("UV-Kat.")

df["uv_raw"].plot(ax=axes[7], legend=False, color="tab:purple")
axes[7].set_ylabel("UV-Raw")

df["uv_api"].plot(ax=axes[8], legend=False, color="tab:cyan")
axes[8].set_ylabel("UV-API")

plt.xlabel("Zeit")
plt.tight_layout()

# Dateinamen mit Datum und Zeit
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"innen_und_aussen_und_uv_subplots_{timestamp}.png"
plt.savefig(filename, dpi=150)
