import pandas as pd                # Datenanalyse-Bibliothek
import matplotlib.pyplot as plt    # Für Diagramme
from datetime import datetime      # Für Zeitstempel

df = pd.read_csv("innen.csv", parse_dates=["timestamp"]).set_index("timestamp")  # CSV einlesen, Zeitstempel als Index
    #df ist die ganze Tabelle; df["spaltenname"] ist eine einzelne Spalte daraus.

fig, axes = plt.subplots(9, 1, sharex=True, figsize=(10, 18))  # 9 Diagramme untereinander, gleiche x-Achse
    # 9 Zeilen, 1 Spalte; also 9 Diagramme (Subplots) untereinander.
    # fig ist das ganze Bild, axes sind die einzelnen Unterdiagramme (Subplots)
    # sharex = alle benutzen die gleiche x-Achse.

# "Zeichne die Werte aus der Spalte „temp_c“ als Linie in das erste Diagramm"
df["temp_c"].plot(ax=axes[0], legend=False, color="tab:red")    # Temperatur innen (rot)
axes[0].set_ylabel("Innen °C")                                 # y-Achse beschriften
    # Legende aus
    # Mit ax=axes[...] wird festgelegt, in welches Unterdiagramm (subplot) die Linie gezeichnet wird.
    # ax=... ist eine Konvention von matplotlib (und pandas nutzt das mit)?

df["temp_out"].plot(ax=axes[1], legend=False, color="tab:orange")  # Temperatur außen (orange)
axes[1].set_ylabel("Außen °C")

df["hum_rel"].plot(ax=axes[2], legend=False, color="tab:blue")     # Luftfeuchte innen (blau)
axes[2].set_ylabel("Innen % rF")

df["hum_out"].plot(ax=axes[3], legend=False, color="tab:green")    # Luftfeuchte außen (grün)
axes[3].set_ylabel("Außen % rF")

df["eco2_ppm"].plot(ax=axes[4], legend=False, color="tab:gray")     # CO₂-Gehalt (grau)
axes[4].set_ylabel("eCO₂ ppm")

df["iaq"].plot(ax=axes[5], legend=False, color="tab:brown")        # Luftqualitätsindex (braun)
axes[5].set_ylabel("IAQ")

df["uv_kategorie"].plot(ax=axes[6], legend=False, color="tab:pink") # UV-Kategorie (pink)
axes[6].set_ylabel("UV-Kat.")

df["uv_raw"].plot(ax=axes[7], legend=False, color="tab:purple")     # UV-Rohwert (lila)
axes[7].set_ylabel("UV-Raw")

df["uv_api"].plot(ax=axes[8], legend=False, color="tab:cyan")       # UV-Wert API (türkis)
axes[8].set_ylabel("UV-API")

plt.xlabel("Zeit")            # x-Achse beschriften
plt.tight_layout()            # Layout anpassen

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")           # Aktuelles Datum/Uhrzeit für Dateinamen
filename = f"innen_und_aussen_und_uv_subplots_{timestamp}.png"     # Dateiname erzeugen

plt.savefig(filename, dpi=150)     # Grafik speichern
