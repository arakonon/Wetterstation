# datenbank.py
import csv, datetime, math, time
from pathlib import Path


class Datenbank:
    """Puffert Innenwerte, mittelt sie über 5 min
       und loggt sie zusammen mit dem letzten ESP-Wert."""

    def __init__(self, logfile="~/Wetterstation/logs/innen.csv",
                 interval_sec=300):
        self.LOGFILE = Path(logfile).expanduser()
        self.LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        self.INTERVAL = interval_sec

        # Puffer für Innenwerte
        self._sum_iaq = self._sum_co2 = 0.0
        self._sum_hum = self._sum_temp = 0.0
        self._count = 0

        # Letzter ESP-Wert
        self._ext_temp = None
        self._ext_hum = None
        self._last_write = time.time()

        self._header = [
            "timestamp", "iaq", "co2_ppm",
            "hum_rel", "temp_c",
            "temp_out", "hum_out"
        ]

    # ---------- öffentliche API ----------
    def log_row(self, sensor, temp_out=None, hum_out=None):
        """Alle 30 s aufrufen. Schreibt erst nach 300 s eine Zeile."""

        # Innenmessung in den Puffer
        iaq, _ = sensor.read_iaq()
        co2, _ = sensor.read_co2()
        self._sum_iaq  += iaq
        self._sum_co2  += co2
        self._sum_hum  += sensor.read_humidity()
        self._sum_temp += sensor.read_temperature()
        self._count    += 1

        # Neueste Außenwerte merken (falls vorhanden)
        if temp_out is not None:
            self._ext_temp = temp_out
        if hum_out is not None:
            self._ext_hum  = hum_out

        # Ist das Intervall abgelaufen?
        now = time.time()
        if now - self._last_write < self.INTERVAL:
            return  # noch warten – nichts schreiben

        # ----- Mittelwerte bilden -----
        if self._count == 0:         # sollte nie passieren
            return
        avg = lambda s: round(s / self._count, 2)

        row = [
            datetime.datetime.now().isoformat(timespec="seconds"),
            avg(self._sum_iaq),
            avg(self._sum_co2),
            avg(self._sum_hum),
            avg(self._sum_temp),
            "" if self._ext_temp is None else round(self._ext_temp, 2),
            "" if self._ext_hum  is None else round(self._ext_hum, 2),
        ]

        # ----- CSV schreiben -----
        write_header = not self.LOGFILE.exists()
        with open(self.LOGFILE, "a", newline="") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(self._header)
            w.writerow(row)

        print("[Datenbank] neue Zeile geschrieben:", row)

        # ----- Puffer zurücksetzen -----
        self._sum_iaq = self._sum_co2 = 0.0
        self._sum_hum = self._sum_temp = 0.0
        self._count = 0
        self._last_write = now
