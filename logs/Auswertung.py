import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("innen.csv", parse_dates=["timestamp"]).set_index("timestamp")

fig, axes = plt.subplots(4, 1, sharex=True, figsize=(10, 8))

df["temp_c"].plot(ax=axes[0], legend=False)
axes[0].set_ylabel("°C")

df["hum_rel"].plot(ax=axes[1], legend=False)
axes[1].set_ylabel("% rF")

df["co2_ppm"].plot(ax=axes[2], legend=False)
axes[2].set_ylabel("ppm")

df["iaq"].plot(ax=axes[3], legend=False)
axes[3].set_ylabel("IAQ")

plt.xlabel("Zeit")
plt.tight_layout()
plt.savefig("innen_subplots.png", dpi=150)   # oder einfach plt.show()
