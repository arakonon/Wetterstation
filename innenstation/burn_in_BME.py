#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import csv
from bme68x import BME68X
import bme68xConstants as cst
import bsecConstants as bsec

def burn_in(sensor,
            duration_hours: float = 24.0,
            sample_rate: int = bsec.BSEC_SAMPLE_RATE_ULP,
            log_file: str = 'burnin_log.csv',
            state_file: str = 'bsec_state.txt'):
    """
    Führt den 24h-Burn-in im angegebenen Sample-Rate-Mode durch,
    loggt IAQ & Accuracy und speichert den BSEC-State zum Schluss.
    """
    # Setze Abtastrate (ULP = 300 s, LP = 3 s, HP = 1 s)
    sensor.set_sample_rate(sample_rate)
    interval = {bsec.BSEC_SAMPLE_RATE_ULP: 300,
                bsec.BSEC_SAMPLE_RATE_LP:    3,
                bsec.BSEC_SAMPLE_RATE_HIGH_PERFORMANCE: 1}[sample_rate]

    total_seconds = duration_hours * 3600
    start_time = time.time()

    # CSV-Logger öffnen
    with open(log_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['timestamp','iaq','iaq_accuracy'])
        writer.writeheader()

        # Burn-in-Schleife
        while True:
            elapsed = time.time() - start_time
            if elapsed >= total_seconds:
                break

            try:
                data = sensor.get_bsec_data()
            except Exception as e:
                print("Sensor noch nicht bereit, retry…", e)
                time.sleep(0.1)
                continue

            if not data:
                time.sleep(0.1)
                continue

            # Je nach Rückgabe-Typ (dict oder tuple) extrahieren
            if isinstance(data, dict):
                iaq = data['iaq']
                acc = data['iaq_accuracy']
            else:
                iaq, acc = data[2], data[3]

            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"[{ts}] IAQ={iaq:.2f}, Accuracy={acc}")
            writer.writerow({'timestamp': ts, 'iaq': iaq, 'iaq_accuracy': acc})

            time.sleep(interval)

    # Zum Schluss BSEC-State speichern
    state = sensor.get_bsec_state()
    with open(state_file, 'w') as f:
        f.write(str(state))
    print(f"✅ Burn-in fertig! BSEC-State in '{state_file}' geschrieben.")


def restore_state(sensor, state_file: str = 'bsec_state.txt'):
    """
    Lädt den zuvor gespeicherten BSEC-State und wendet ihn an.
    """
    with open(state_file, 'r') as f:
        content = f.read().strip()[1:-1].split(',')
        state = [int(x) for x in content]
    sensor.set_bsec_state(state)
    print("🔄 BSEC-State wiederhergestellt.")


def main():
    # Sensor initialisieren (Adresse HIGH=0x77, debug_mode=0)
    sensor = BME68X(cst.BME68X_I2C_ADDR_HIGH, 0)
    print("⭐ Sensor initialisiert. Starte Burn-in…")

    # 24-Stunden-Burn-in
    burn_in(sensor,
            duration_hours=24.0,
            sample_rate=bsec.BSEC_SAMPLE_RATE_ULP,
            log_file='burnin_log.csv',
            state_file='bsec_state.txt')

    # Wenn du später direkt den gespeicherten State laden willst:
    # restore_state(sensor)


if __name__ == "__main__":
    main()
