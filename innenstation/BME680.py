#!/usr/bin/env python3

import json, time, os, sys
import bme68x
import bsecConstants as bsec

# Pfad zur Datei, in der der Kalibrierungszustand des Sensors gespeichert wird
STATE_FILE = os.path.expanduser("~/Wetterstation/innenstation/bsec_iaq_state.json")
SAMPLE_RATE  = bsec.BSEC_SAMPLE_RATE_LP   # Sampling-Rate: Low Power (3 Sekunden Zyklus)
MAX_WAIT_SEC = 10                         # Maximale Wartezeit auf neue Sensordaten (Timeout)

class BME680:
    def __init__(
            self, 
            addr: int = 0x77, 
            temp_offset: float = 0.0):
        # Startzeit merken, um Kalibrierungsdauer zu berechnen
        self._start_t = time.time()        

        # --- Sensor & BSEC Initialisierung --------------------------------------
        # Sensor-Objekt erzeugen, Adresse und BSEC-Modus setzen
        self._sensor = bme68x.BME68X(addr, 1)        # use_bsec = 1
        self._sensor.set_sample_rate(SAMPLE_RATE)    # Sampling-Rate setzen
        self._sensor.disable_debug_mode()            # Debug-Modus deaktivieren
        
        # Temperatur-Offset ggf. setzen (z.B. für Gehäusewärme)
        if temp_offset:
            self._sensor.set_temp_offset(int(round(temp_offset)))

        # --- Kalibrierungs-Status laden ----------------------------------------
        # Prüfen, ob ein gespeicherter State existiert (Kalibrierung)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                self._sensor.set_bsec_state(json.load(f))
                print("State geladen →", STATE_FILE)
        else:
            # Ohne State kann der Sensor nicht sinnvoll arbeiten
            sys.exit("Fehler: Kein State gefunden – erst Burn‑in ausführen!")

        # Letzten Datensatz und Zeitstempel initialisieren
        self._last: dict | None = None   # letzter Datensatz
        self._last_t: float = 0.0        # Zeitstempel des letzten Updates

    # ----------------------------------------------------------------
    def _update(self):
        """Holt neue Daten vom Sensor, falls das Sampling-Intervall abgelaufen ist."""
        # Wenn die letzten Daten noch frisch genug sind, nichts tun
        if time.time() - self._last_t < 3.5 and self._last:
            return  # Daten sind aktuell

        t0 = time.time()  # Startzeit für Timeout
        while True:
            d = self._sensor.get_bsec_data()  # Neue Daten vom Sensor holen
            if d:
                self._last, self._last_t = d, time.time()  # Daten und Zeitstempel speichern
                return
            if time.time() - t0 > MAX_WAIT_SEC:
                # Wenn zu lange keine Daten kommen, Fehler werfen
                raise RuntimeError("Timeout: keine gültigen Sensordaten")
            time.sleep(0.05)  # Kurz warten und erneut versuchen

    # ---- Öffentliche Lesemethoden ----------------------------------
    def read_temperature(self):
        # Holt aktuelle Temperatur vom Sensor (°C)
        self._update()  # Frische Daten holen, falls nötig
        return self._last["temperature"]  # Temperaturwert zurückgeben

    def read_humidity(self):
        # Holt aktuelle Luftfeuchtigkeit (%) vom Sensor
        self._update()
        return self._last["humidity"]

    def read_pressure(self):
        # Holt aktuellen Luftdruck (hPa) vom Sensor
        self._update()
        return self._last["raw_pressure"]

    def read_gas(self):
        # Holt aktuellen Gaswiderstand (Ohm) vom Sensor
        self._update()
        return self._last["raw_gas"]

    # ---- IAQ / CO₂ --------------------------------------------------
    def read_iaq(self):
        # Holt aktuellen IAQ-Wert (Luftqualität) und Genauigkeit
        # Gibt (iaq, acc) zurück, aber nur echten Wert wenn acc >= 2, sonst None
        self._update()
        iaq = self._last["iaq"]
        acc = self._last["iaq_accuracy"]
        return (iaq if acc >= 2 else None, acc)

    def read_co2(self):
        # Holt aktuellen CO₂-Äquivalent-Wert und Genauigkeit
        # Gibt (co2, acc) zurück, aber nur echten Wert wenn acc >= 2, sonst None
        self._update()
        co2 = self._last["co2_equivalent"]
        acc = self._last["co2_accuracy"]
        return (co2 if acc >= 2 else None, acc)

    # ---- Convenience-Strings ---------------------------------------
    def iaq_str(self):
        # Gibt einen formatierten String für den IAQ-Wert zurück.
        # Zeigt Kalibrierungsdauer, falls accuracy < 2.

        iaq, acc = self.read_iaq()
        if acc < 2:
            mins = int((time.time() - self._start_t) // 60)
            return f"Kalibrierung seit: {mins:02d} Minuten"
        return f"{iaq:.1f} (Acc {acc})"

    def co2_str(self):
        # Gibt einen formatierten String für den CO₂-Wert zurück.
        # Zeigt Kalibrierungsdauer, falls accuracy < 2.
        
        co2, acc = self.read_co2()
        if acc < 2:
            mins = int((time.time() - self._start_t) // 60)
            return f"Kalibrierung seit: {mins:02d} Minuten"
        return f"{int(co2)} ppm (Acc {acc})"
    
    #---- Convenience-Strings für LCD -------------------------------
    def iaq_str_LCD(self):
        # Kurzer String für LCD-Anzeige: IAQ oder Kalibrierung.
        iaq, acc = self.read_iaq()
        if acc < 2:
            mins = int((time.time() - self._start_t) // 60)
            return "Kalibr. seit"
        return f"  :{int(iaq)}"

    def co2_str_LCD(self):
        # Kurzer String für LCD-Anzeige: CO₂ oder Kalibrierungszeit.
        co2, acc = self.read_co2()
        if acc < 2:
            mins = int((time.time() - self._start_t) // 60)
            return f"{mins:02d}m"
        return f"{int(co2)}"
    # ----------------------------------------------------------------
    def save_state(self):
        # Speichert den aktuellen Kalibrierungszustand des Sensors.
        # Nur wenn Accuracy == 3 (maximale Genauigkeit erreicht).
        acc = self._last.get("iaq_accuracy", 0) if self._last else 0
        if acc == 3:
            with open(STATE_FILE, "w") as f:
                json.dump(self._sensor.get_bsec_state(), f)
            print("State gespeichert →", STATE_FILE)
        else:
            print("Accuracy < 3 – State nicht gespeichert.")

    def close(self):
        #Speichert den State und schließt die I2C-Verbindung.
        self.save_state()
        self._sensor.close_i2c()
