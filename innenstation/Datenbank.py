# datenbank.py
import csv, datetime, math, time
from pathlib import Path


class Datenbank:
    #Puffert Innenwerte, mittelt sie über 5 min und loggt sie zusammen mit dem letzten ESP-Wert

    def __init__(self, logfile="~/Wetterstation/logs/innen.csv",
                 interval_sec=300):
        # Logdatei-Pfad vorbereiten, ggf. Verzeichnisse anlegen
        self.LOGFILE = Path(logfile).expanduser()
        self.LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        self.INTERVAL = interval_sec  # Intervall für Mittelwert/Schreibvorgang (Sekunden)

        # Puffer für Innenwerte initialisieren
        self._sum_iaq = self._sum_co2 = 0.0
        self._sum_hum = self._sum_temp = 0.0
        self._count = 0  # Anzahl gültiger Messungen im aktuellen Intervall

        # Außenwerte
        self._ext_temp = None
        self._ext_hum = None
        self._ext_uv = None  
        self._ext_uv_raw = None
        self._ext_uv_api = None    
        self._last_write = time.time()  # Zeitstempel des letzten Schreibvorgangs

        # CSV-Header für die Logdatei
        self._header = [
            "timestamp", "iaq", "co2_ppm",
            "hum_rel", "temp_c",
            "temp_out", "hum_out", "uv_kategorie", "uv_raw", "uv_api"  
        ]

        

    # Hauptfunktion zum Puffern und Schreiben der Messwerte
    def log_row(self, sensor, temp_out=None, hum_out=None, uv_kat=None, uv_raw=None, uv_api=None):  
        # Holt aktuelle Innenwerte vom Sensor und summiert sie für die Mittelwertbildung
        iaq, _ = sensor.read_iaq()
        co2, _ = sensor.read_co2()
        hum = sensor.read_humidity()
        temp = sensor.read_temperature()
        valid = False                                   
        if iaq is not None and not math.isnan(iaq):
            self._sum_iaq += iaq;          valid = True
        if co2 is not None and not math.isnan(co2):
            self._sum_co2 += co2;          valid = True
        if hum is not None and not math.isnan(hum):
            self._sum_hum += hum;          valid = True
        if temp is not None and not math.isnan(temp):
            self._sum_temp += temp;        valid = True
        if valid:                                       
            self._count += 1  # Nur wenn mindestens ein Wert gültig ist

        # Neueste Außenwerte merken
        if temp_out is not None:
            self._ext_temp = temp_out
        if hum_out is not None:
            self._ext_hum  = hum_out
        if uv_kat is not None:
            self._ext_uv = uv_kat
        if uv_raw is not None:
            self._ext_uv_raw = uv_raw
        if uv_api is not None:                
            self._ext_uv_api = uv_api         

        # Prüfen, ob das Intervall abgelaufen ist – nur dann schreiben
        now = time.time()
        if now - self._last_write < self.INTERVAL:
            return  # Noch nicht genug Zeit vergangen, nichts tun

        # Mittelwerte berechnen, falls mindestens eine Messung vorliegt
        if self._count == 0:         # Sollte eigentlich nie passieren
            return
        avg = lambda s: round(s / self._count, 2)

        # Zeile für CSV-Datei zusammenbauen
        row = [
            datetime.datetime.now().isoformat(timespec="seconds"),
            avg(self._sum_iaq),
            avg(self._sum_co2),
            avg(self._sum_hum),
            avg(self._sum_temp),
            "" if self._ext_temp is None else round(self._ext_temp, 2),
            "" if self._ext_hum  is None else round(self._ext_hum, 2),
            "" if self._ext_uv   is None else round(self._ext_uv, 2),
            "" if getattr(self, '_ext_uv_raw', None) is None else int(self._ext_uv_raw),
            "" if self._ext_uv_api is None else round(self._ext_uv_api, 2)  
        ]

        # CSV-Datei öffnen und ggf. Header schreiben
        write_header = not self.LOGFILE.exists()
        with open(self.LOGFILE, "a", newline="") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(self._header)
            w.writerow(row)

        print("[Datenbank] neue Zeile geschrieben:", row)

        # Puffer zurücksetzen für das nächste Intervall
        self._sum_iaq = self._sum_co2 = 0.0
        self._sum_hum = self._sum_temp = 0.0
        self._count = 0
        self._last_write = now
