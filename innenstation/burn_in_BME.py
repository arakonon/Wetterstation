#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from bme68x import BME68X
import bme68xConstants as cst
import bsecConstants  as bsec

def restore_state(sensor, state_file: str = 'bsec_state.txt'):
    with open(state_file, 'r') as f:
        content = f.read().strip()[1:-1].split(',')
        state = [int(x) for x in content]
    sensor.set_bsec_state(state)
    print("🔄 BSEC-State wiederhergestellt.")

def get_valid_bsec_data(sensor):
    while True:
        try:
            data = sensor.get_bsec_data()
        except Exception:
            time.sleep(0.1)
            continue
        if data:
            return data
        time.sleep(0.1)

def main():
    # Sensor initialisieren
    sensor = BME68X(cst.BME68X_I2C_ADDR_HIGH, 0)
    # Sample-Rate auf LP (3 s) setzen
    sensor.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP)

    # **Hier State laden**
    restore_state(sensor, state_file='bsec_state.txt')

    print("✓ Sensor bereit (Accuracy sollte > 0 sein). Starte Messungen...\n")

    # Hauptschleife
    while True:
        data = get_valid_bsec_data(sensor)
        # Je nach Rückgabetyp dict oder tuple...
        if isinstance(data, dict):
            iaq, acc = data['iaq'], data['iaq_accuracy']
        else:
            iaq, acc = data[2], data[3]

        print(f"IAQ: {iaq:.2f}  (Accuracy: {acc})")
        time.sleep(3)

if __name__ == "__main__":
    main()
