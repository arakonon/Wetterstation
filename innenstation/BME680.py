import json, time, os, sys
import bme68x
import bsecConstants as bsec

# Pfad zur Datei, in der der Kalibrierungszustand des Sensors gespeichert wird
STATE_FILE = os.path.expanduser("~/Wetterstation/innenstation/bsec_iaq_state.json")
    # .expanduser() Ersetzt ein das im Pfad durch das Home-Verzeichnis.
SAMPLE_RATE  = bsec.BSEC_SAMPLE_RATE_LP   # Sampling-Rate: Low Power (3 Sekunden Zyklus)
MAX_WAIT_SEC = 10                         # Maximale Wartezeit auf neue Sensordaten (Timeout)

class BME680:
    def __init__(
            self, 
            addr: int = 0x77, 
            temp_offset: float = 0.0):
        # Startzeit merken, um Kalibrierungsdauer zu berechnen
        self.startT = time.time()        

        # --- Sensor & BSEC Initialisierung ---
        # Sensor-Objekt erzeugen, Adresse und BSEC-Modus setzen
        self.sensor = bme68x.BME68X(addr, 1)        # use_bsec = 1
        self.sensor.set_sample_rate(SAMPLE_RATE)    # Sampling-Rate setzen
        self.sensor.disable_debug_mode()            # Debug-Modus deaktivieren
        
        # Temperatur-Offset Ja/Nein
        if temp_offset:
            self.sensor.set_temp_offset(int(round(temp_offset))) #  erwartet einen ganzzahligen Offset
                # round(temp_offset) rundet den übergebenen Gleitkomma-Wert auf die nächste Ganzzahl
                # int(...) wandelt das Ergebnis (das von round als Float kommt) in einen Integer um.

        # --- Kalibrierungs-Status laden ---
        # Prüfen, ob ein gespeicherter State existiert (Kalibrierung)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                # Erzeugt einen Context Manager.
                # f ist das geöffnete File-Objekt.
                self.sensor.set_bsec_state(json.load(f))
                # "If the state file was written to file [...] for get_bsec_state() 
                # then it will need to be read and processed from a string to an array of Int." -bme68x-python-library

                print("State geladen →", STATE_FILE)
        else:
            # Ohne State kann der Sensor nicht in kurzer Zeit sinnvoll arbeiten und würde Stunden brauchen
            sys.exit("Fehler: Kein State gefunden – erst Burn-in, oder so, ausführen!")

        # Letzten Datensatz und Zeitstempel initialisieren
        self.last = None # Wird zum Dictionary/ HashMap(java)
        self.lastT = 0.0

    # ----------------------------------------------------------------
    def update(self):
        # Holt neue Daten vom Sensor, falls das Sampling-Intervall abgelaufen ist.
        # Wenn die letzten Daten noch frisch genug sind, nichts tun
        if time.time() - self.lastT < 3.5 and self.last:
            return  # Daten sind aktuell

        t0 = time.time()  # Startzeit für Timeout
        while True:
            d = self.sensor.get_bsec_data()  # Neue Daten vom Sensor holen
                # liefert entweder ein Datentupel (truthy) oder None.
            if d: # Sobald d nicht None ist
                # kann zwischen „echten“ Daten und None unterscheiden.
                self.last, self.lastT = d, time.time()  # Daten und Zeitstempel speichern
                return
            if time.time() - t0 > MAX_WAIT_SEC:
                # Wenn zu lange keine Daten kommen, Fehler werfen
                raise RuntimeError("Timeout: keine gültigen Sensordaten")
            time.sleep(0.05)  # Kurz warten und erneut versuchen

    # ---- Öffentliche Lesemethoden ----------------------------------
    def read_temperature(self):
        # Holt aktuelle Temperatur vom Sensor (°C)
        self.update()  # Frische Daten holen, falls nötig
        return self.last["temperature"]  # Temperaturwert zurückgeben

    def read_humidity(self):
        # Holt aktuelle Luftfeuchtigkeit (%) vom Sensor
        self.update()
        return self.last["humidity"]

    def read_pressure(self):
        # Holt aktuellen Luftdruck (hPa) vom Sensor
        self.update()
        return self.last["raw_pressure"]

    def read_gas(self):
        # Holt aktuellen Gaswiderstand (Ohm) vom Sensor
        self.update()
        return self.last["raw_gas"]

    # ---- IAQ / eCO₂ --------------------------------------------------
    def read_iaq(self):
        # Holt aktuellen IAQ-Wert (Luftqualität) und Genauigkeit
        # Gibt (iaq, acc) zurück, aber nur echten Wert wenn acc >= 2, sonst None
        self.update()
        iaq = self.last["iaq"]
        acc = self.last["iaq_accuracy"]
        return (iaq if acc >= 2 else None, acc) # Schon ab accuracy 2 in der Konsole ausgeben
            # return ((iaq if acc >= 2 else None), acc)
            # if acc >= 2:
            #     return (iaq, acc)
            # else:
            #     return (None, acc)

    def read_eco2(self):
        # Holt aktuellen CO₂-Äquivalent-Wert und Genauigkeit
        # Gibt (eco2, acc) zurück, aber nur echten Wert wenn acc >= 2, sonst None
        self.update()
        eco2 = self.last["co2_equivalent"]
        acc = self.last["co2_accuracy"]
        return (eco2 if acc >= 2 else None, acc)

    # ---- Convenience-Strings ---------------------------------------
    def iaq_str(self):
        # Gibt einen formatierten String für den IAQ-Wert zurück.
        # Zeigt Kalibrierungsdauer, falls accuracy < 2.

        iaq, acc = self.read_iaq()
        if acc < 1:
            mins = int((time.time() - self.startT) // 60)
            return f"Acc: {int(acc)} Kalibrierung seit: {mins:02d} Minuten"
        return f"{iaq:.1f} (Acc {acc})"

    def eco2_str(self):
        # Gibt einen formatierten String für den eCO₂-Wert zurück.
        # Zeigt Kalibrierungsdauer, falls accuracy < 2.
        
        eco2, acc = self.read_eco2()
        if acc < 1:
            mins = int((time.time() - self.startT) // 60)
            return f"Acc: {int(acc)} Kalibrierung seit: {mins:02d} Minuten"
        return f"{int(eco2)} ppm (Acc {acc})"
    
    #---- Convenience-Strings für LCD -------------------------------
    def iaq_str_LCD(self):
        # Kurzer String für LCD-Anzeige: IAQ oder Kalibrierung.
        iaq, acc = self.read_iaq()
        if acc <= 2:
            mins = int((time.time() - self.startT) // 60)
            return "Kalibr. seit"
        return f"  {int(iaq)}"

    def eco2_str_LCD(self):
        # Kurzer String für LCD-Anzeige: CO₂ oder Kalibrierungszeit.
        eco2, acc = self.read_eco2()
        if acc <= 2:
            mins = int((time.time() - self.startT) // 60)
            return f"{mins:02d}m"
        return f"{int(eco2)}"
    # ----------------------------------------------------------------
    def save_state(self):
        # Speichert den aktuellen Kalibrierungszustand des Sensors.
        # Nur wenn Accuracy == 3 (maximale Genauigkeit erreicht).
        acc = self.last.get("iaq_accuracy", 0) if self.last else 0
            # Hohlt den letzten acc Stand, wenn dieser nicht existiert; Rückfall-Wert 0
            # Wenn self.last nicht truthly ist (nicht existiert(None ist)), auch 0

        if acc == 3:
            with open(STATE_FILE, "w") as f:
                json.dump(self.sensor.get_bsec_state(), f)
                # Erzeugt einen Context Manager.
                # f ist das geöffnete File-Objekt.
                    # öffnet die Datei im Schreib-Modus ("w", also alte Inhalte werden überschrieben)
                    # wandelt das von get_bsec_state() zurückgelieferte Python-Objekt in einen JSON-String um
                    # und schreibt diesen String komplett in die Datei.
                # json.dump(obj, f) serialisiert obj und schreibt den JSON-Text in das geöffnete File-Objekt f.
                    # Intern ruft es dabei f.write(...) auf.

            print("State gespeichert →", STATE_FILE)
        else:
            print("Accuracy < 3 – State nicht gespeichert.")

    def close(self):
        #Speichert den State und schließt die I2C-Verbindung.
        self.save_state()
        self.sensor.close_i2c()
