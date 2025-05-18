import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("innen.csv", parse_dates=["timestamp"]).set_index("timestamp")

fig, axes = plt.subplots(6, 1, sharex=True, figsize=(10, 12))

df["temp_c"].plot(ax=axes[0], legend=False)
axes[0].set_ylabel("Innen °C")

df["temp_out"].plot(ax=axes[1], legend=False, color="tab:orange")
axes[1].set_ylabel("Außen °C")

df["hum_rel"].plot(ax=axes[2], legend=False)
axes[2].set_ylabel("Innen % rF")

df["hum_out"].plot(ax=axes[3], legend=False, color="tab:green")
axes[3].set_ylabel("Außen % rF")

df["co2_ppm"].plot(ax=axes[4], legend=False)
axes[4].set_ylabel("CO₂ ppm")

df["iaq"].plot(ax=axes[5], legend=False)
axes[5].set_ylabel("IAQ")

plt.xlabel("Zeit")
plt.tight_layout()
plt.savefig("innen_und_aussen_subplots.png", dpi=150)
