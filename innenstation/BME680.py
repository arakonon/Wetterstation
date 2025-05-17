#!/usr/bin/env python3

import json, time, os, sys
import bme68x
import bsecConstants as bsec

STATE_FILE = os.path.expanduser("~/Wetterstation/innenstation/bsec_iaq_state.json")
SAMPLE_RATE  = bsec.BSEC_SAMPLE_RATE_LP   # 3‑Sek‑Zyklus
MAX_WAIT_SEC = 10                         # maximale Wartezeit auf Daten

class BME680:
    def __init__(
            self, 
            addr: int = 0x77, 
            temp_offset: float = 0.0):
        
        self._start_t = time.time()        # ⏱ Zeitstempel für Laufzeit‑Info

        # --- Sensor & BSEC Init --------------------------------------
        self._sensor = bme68x.BME68X(addr, 1)        # use_bsec = 1
        self._sensor.set_sample_rate(SAMPLE_RATE)
        self._sensor.disable_debug_mode()
        
        # temp offset in bsec einbinden
        if temp_offset:
            self._sensor.set_temp_offset(int(round(temp_offset)))

        # --- Kalibrier‑State laden -----------------------------------
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                self._sensor.set_bsec_state(json.load(f))
                print("State geladen →", STATE_FILE)
        else:
            sys.exit("Fehler: Kein State gefunden – erst Burn‑in ausführen!")

        self._last: dict | None = None   # letzter Datensatz
        self._last_t: float = 0.0        # Zeitstempel des letzten Updates

    # ----------------------------------------------------------------
    def _update(self):
        """Holt neue Daten, falls Sampling‑Intervall abgelaufen."""
        if time.time() - self._last_t < 3.5 and self._last:
            return  # noch aktuell

        t0 = time.time()
        while True:
            d = self._sensor.get_bsec_data()
            if d:
                self._last, self._last_t = d, time.time()
                return
            if time.time() - t0 > MAX_WAIT_SEC:
                raise RuntimeError("Timeout: keine gültigen Sensordaten")
            time.sleep(0.05)

    # ---- Öffentliche Lesemethoden ----------------------------------
    def read_temperature(self):
        self._update()
        return self._last["temperature"]

    def read_humidity(self):
        self._update()
        return self._last["humidity"]

    def read_pressure(self):
        self._update()
        return self._last["raw_pressure"]

    def read_gas(self):
        self._update()
        return self._last["raw_gas"]

    # ---- IAQ / CO₂ --------------------------------------------------
    def read_iaq(self):
        """→ (iaq | None, accuracy)"""
        self._update()
        iaq, acc = self._last["iaq"], self._last["iaq_accuracy"]
        return (iaq if acc >= 2 else None, acc)

    def read_co2(self):
        """→ (co2_aeq | None, accuracy)"""
        self._update()
        co2, acc = self._last["co2_equivalent"], self._last["co2_accuracy"]
        return (co2 if acc >= 2 else None, acc)

    # ---- Convenience‑Strings ---------------------------------------
    def iaq_str(self):
        iaq, acc = self.read_iaq()
        if acc < 2:
            mins = int((time.time() - self._start_t) // 60)
            return f"Kalibrierung seit: {mins:02d} Minuten"
        return f"{iaq:.1f} (Acc {acc})"

    def co2_str(self):
        co2, acc = self.read_co2()
        if acc < 2:
            mins = int((time.time() - self._start_t) // 60)
            return f"Kalibrierung seit: {mins:02d} Minuten"
        return f"{int(co2)} ppm (Acc {acc})"
    
    #---- Convenience‑Strings für LCD -------------------------------
    def iaq_str_LCD(self):
        iaq, acc = self.read_iaq()
        if acc < 2:
            mins = int((time.time() - self._start_t) // 60)
            return "Kalibr. seit"
        return f"  :{int(iaq)}"

    def co2_str_LCD(self):
        co2, acc = self.read_co2()
        if acc < 2:
            mins = int((time.time() - self._start_t) // 60)
            return f"{mins:02d}m"
        return f"{int(co2)}"
    # ----------------------------------------------------------------
    def save_state(self):
        """Schreibt den State nur, wenn Accuracy == 3."""
        acc = self._last.get("iaq_accuracy", 0) if self._last else 0
        if acc == 3:
            with open(STATE_FILE, "w") as f:
                json.dump(self._sensor.get_bsec_state(), f)
            print("State gespeichert →", STATE_FILE)
        else:
            print("Accuracy < 3 – State nicht gespeichert.")

    def close(self):
        self.save_state()
        self._sensor.close_i2c()
