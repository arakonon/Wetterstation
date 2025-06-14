from checkQuality import checkQuality
import csv, datetime, math, time
from pathlib import Path # Für zugriff auf Dateien
    # os; os.path wollte irgendwie nicht Funktionieren


class Datenbank:
    #Puffert Innenwerte, mittelt sie über 5 min und loggt sie zusammen mit dem letzten ESP-Wert

    def __init__(self, logfile="~/Wetterstation/logs/innen.csv",
                 intervalSec=300):
        # Logdatei-Pfad vorbereiten, ggf. Verzeichnisse anlegen (wird in "with open" gemacht)
        self.logFile = Path(logfile).expanduser()
        Path(logfile)
            # Erzeugt ein pathlib.Path-Objekt aus dem String logfile.
            # .expanduser() Ersetzt ein das im Pfad durch das Home-Verzeichnis.
        self.interval = intervalSec  # Intervall für Mittelwert/Schreibvorgang (Sekunden)

        # Puffer für Innenwerte initialisieren
        self.sumIaq = self.sumEco2 = 0.0
        self.sumHum = self.sumTemp = 0.0
        self.countIaq = self.countEco2 = 0
        self.countHum = self.countTemp = 0

        # Außenwerte
        self.extTemp = None
        self.extHum = None
        self.extUv = None
        self.extUvRaw = None
        self.extUvApi = None
        self.lastWrite = time.time()  # Zeitstempel des letzten Schreibvorgangs

        # CSV-Header für die Logdatei
        self.header = [
            "timestamp", "iaq", "eco2_ppm",
            "hum_rel", "temp_c",
            "temp_out", "hum_out", "uv_kategorie", "uv_raw", "uv_api"
        ]

        self.check = checkQuality()


    # Hauptfunktion zum Puffern und Schreiben der Messwerte
    def logRow(self, sensor, tempOut=None, humOut=None, uvKat=None, uvRaw=None, uvApi=None):  
        # Es wird in jedem Aufruf von logRow entscheieden, ob und welche Außen­werte übergeben werden. Wegen Parametern.
        
        # Holt aktuelle Innenwerte vom Sensor und summiert sie für die Mittelwertbildung
        iaq, acc = sensor.readIaq()
        eco2, _ = sensor.readEco2()
        hum = sensor.readHumidity()
        temp = sensor.readTemperature()
        valid = False

        if self.check.isPlausible(iaq, 0, 500): #and acc > 2: # Einkommentieren, wenn nicht geloggt werden soll, wenn acc sinkt
            self.sumIaq += iaq
            self.countIaq += 1
        if self.check.isPlausible(eco2, 0, 5000): #and acc > 2:
            self.sumEco2 += eco2
            self.countEco2 += 1
        if self.check.isPlausible(hum, 10, 90):
            self.sumHum += hum
            self.countHum += 1
        if self.check.isPlausible(temp, 9, 40):
            self.sumTemp += temp
            self.countTemp += 1
            
      
        # Neueste Außenwerte merken
        # Müssen nicht gemittelt werden, weil der Esp auch nur jede 5 Minuten sendet.
        self.extTemp = tempOut
        self.extHum = humOut
        self.extUv = uvKat
        self.extUvRaw = uvRaw
        self.extUvApi = uvApi

        # Prüfen, ob das Intervall abgelaufen ist – nur dann schreiben
        now = time.time()
        if now - self.lastWrite < self.interval:
            return  # Noch nicht genug Zeit vergangen, nichts tun

        # Mittelwerte berechnen, falls mindestens eine Messung vorliegt
        if self.countIaq == 0 and self.countEco2 == 0 and self.countHum == 0 and self.countTemp == 0:
            return
        

        # Zeile für CSV-Datei zusammenbauen
        row = [
            datetime.datetime.now().isoformat(timespec="seconds"),
                # datetime.datetime.now() liefert die aktuelle Uhrzeit inklusive Datum als datetime-Objekt
                # isoformat(timespec="seconds") wandelt das datetime-Objekt in einen ISO-8601-String um
                # timespec="seconds" entfernt Mikrosekunden.
            self.avg(self.sumIaq, self.countIaq),
            self.avg(self.sumEco2, self.countEco2),
            self.avg(self.sumHum, self.countHum),
            self.avg(self.sumTemp, self.countTemp),

            # Round nur, damit max 2 Nachkommastellen
            # extra Check für "" und nicht "-"
            "" if self.extTemp is None or not isinstance(self.extTemp, (int, float)) else round(self.extTemp, 2),
                # Wenn self.extTemp is None, wird "" (leerer String) in die CSV-Zeile geschrieben.
                # und wenn extTemp nicht int oder float ist ("---")
                # Ansonsten round(self.extTemp, 2).
            # Das gleiche hier:
            "" if self.extHum is None or not isinstance(self.extHum, (int, float)) else round(self.extHum, 2),
            "" if self.extUv is None or not isinstance(self.extUv, (int, float)) else round(self.extUv, 2),
            "" if self.extUvRaw is None or not isinstance(self.extUvRaw, (int, float)) else round(self.extUvRaw, 2),
            "" if self.extUvApi is None or not isinstance(self.extUvApi, (int, float)) else round(self.extUvApi, 2)
        ]

        # CSV-Datei öffnen und ggf. Header schreiben
        writeHeader = not self.logFile.exists() # writeHeader ist True, wenn die Datei noch nicht existiert. (Sollte nicht passieren)
            # Die Methode .exists() stammt vom Path–Objekt aus dem pathlib Modul

        # siehe https://docs.python.org/3/library/csv.html
        with open(self.logFile, "a", newline="") as f:
            # with … as f:
                # Erzeugt einen Context Manager.
                # f ist das geöffnete File-Objekt.
                # Am Ende des Blocks wird f.close() automatisch aufgerufen (auch bei Fehlern).
            # open(self.logFile, "a", newline="")
                # Öffnet die Datei unter self.logFile.
                # Modus "a" heißt append: neue Zeilen werden angehängt.
                # newline="" deaktiviert interne Übersetzung von Zeilen­enden – wichtig, damit csv.writer keine leeren Zeilen einfügt?
            w = csv.writer(f) # Erzeugt einen CSV-Writer, der f für Ausgaben nutzt.
            if writeHeader: # Wenn writeHeader == True (Datei neu), wird zuerst die Kopf­zeile mit Spaltennamen geschrieben.
                w.writerow(self.header)
            w.writerow(row) # Schreibt die Datenzeile in die CSV Datei.

        print("[Datenbank] neue Zeile geschrieben:", row)

        # Puffer zurücksetzen für das nächste Intervall
        self.sumIaq = self.sumEco2 = 0.0
        self.sumHum = self.sumTemp = 0.0
        self.countIaq = self.countEco2 = 0
        self.countHum = self.countTemp = 0
        self.lastWrite = now

    def avg(self, w, c):
        return "" if w == 0 else round(w / c, 2)
        # round((wert / count) = x), 2) liefert x gerundet auf 2 Dezimalstellen.
