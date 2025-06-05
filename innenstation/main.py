#!/usr/bin/env python3

from lcd import LcdControl, lcdCheck
from BME680 import BME680
from Mqtt import EspAußen, MQTTPublisher
#from LegacyCode.Buzzer import Buzzer
from Ampel import Ampel
from Datenbank import Datenbank
from UvApi import UvApiClient
import time, os
import threading

# Sensor- und Steuerungsobjekte initialisieren
bme = BME680(temp_offset=-0.1)      # BME680-Sensor mit Temperatur-Offset
ampel = Ampel(bme)                  # Ampel-Logik mit Sensor
lcd = LcdControl()                  # LCD-Anzeige
button = lcdCheck()                 # Thread für Button-Steuerung (Menüumschaltung)
speicher = Datenbank()              # Datenbank/Logger für Mittelwerte
esp = EspAußen(host="127.0.0.1", timeout=600)  # ESP32 Außenstation
mqtt = MQTTPublisher()              # MQTT Publisher (für OpenHAB)
uvApi = UvApiClient()               # UV-API-Client für aktuelle UV-Werte

def main():
    # Initialisierung und Start aller Threads und Komponenten
    ampel.ampelt_test()  # Teste die Ampelsteuerung (LEDs durchschalten)
    ampel_thread = threading.Thread(target=ampel.start)  # Ampel in eigenem Thread starten
    ampel_thread.start()
    button.start()  # Button-Thread starten (für Menüumschaltung)
    next_log = time.time() + 30 # Erster Log nach 30 Sekunden
    print("warte auf Sensor-Daten")

    # Haupt-Loop: läuft bis zum Abbruch (Strg+C)
    try:
        while True:
            # Sensorwerte holen (innen & außen)
            iaq, acc = bme.read_iaq()  # IAQ-Wert (und Genauigkeit)
            tAußen = esp.get("temperature")  # Außentemperatur
            hAußen = esp.get("humidity")     # Außenfeuchte
            tATxt = esp.get_str("temperature", unit="°C")  # Außentemperatur als String
            hATxt = esp.get_str("humidity"   , unit="%rF") # Außenfeuchte als String
            sonnenWert = esp.get("sun_raw")                # Sonnenwert (Rohwert)
            sonnenKategorie = esp.get("sun_kategorie")     # Sonnenkategorie (1-4)
            uv = uvApi.get_current_uv()                    # UV-Wert von API

            # LCD-Ausgabe je nach Button-Zustand (Menü)
            if button.zustand == 0:
                lcd.lcd.backlight_enabled = True  # Hintergrundbeleuchtung an
                if acc < 2:
                    # Sensor noch nicht kalibriert: Kalibrierungsanzeige
                    lcd.display_calibration(bme.read_temperature(), bme.read_humidity(),
                                            bme.iaq_str_LCD(), bme.co2_str_LCD())
                else:
                    # Sensor kalibriert: Messwerte anzeigen
                    lcd.display_measurement(bme.read_temperature(), bme.read_humidity(),
                                            bme.iaq_str_LCD(), bme.co2_str_LCD())
            elif button.zustand == 1:
                lcd.lcd.backlight_enabled = True
                if not esp.is_alive():
                    # Außenstation nicht erreichbar
                    lcd.display_text("Aussenstation:",  "Connection Lost")
                else:
                    # Außenwerte und UV anzeigen
                    lcd.display_text(f"Aussen: UV:{uv}", f"{tATxt} {hATxt}")
                    lcd.sunSymbol(sonnenKategorie)  # Sonnen-Symbol je nach Kategorie

            elif button.zustand == 2:
                # Display aus (bisschen Strom sparen)
                lcd.lcd.backlight_enabled = False

            # Terminal-Ausgabe (Debug/Monitoring)
            print("\nTemperatur: %0.1f °C" % bme.read_temperature())
            print("Luftfeuchtigkeit: %0.1f %%" % bme.read_humidity())
            print("Luftqualität:", bme.iaq_str())
            print("CO₂-Äquivalent:", bme.co2_str())
            if not esp.is_alive():
                print("Außen-Station: connection lost")
            else:
                print(f"\nAußen: Temperatur; {tATxt}  Hum; {hATxt}")
                print(f"Sun: raw; {sonnenWert} Kategorie {sonnenKategorie}")
                print(f"UV-Wert von API: {uv}")

            # MQTT-Publish für OpenHAB
            werte = {
                "temp": bme.read_temperature(),
                "hum": bme.read_humidity(),
                "iaq": bme.read_iaq()[0],
                "co2": bme.read_co2()[0],
                "uvApi": uv,
            }
            mqtt.publish(werte)
            
            # Datenbank-Logging: alle 30 Sekunden Mittelwerte speichern
            if time.time() >= next_log:         
                speicher.log_row(
                    bme,
                    tAußen,
                    hAußen,
                    sonnenKategorie,
                    sonnenWert,
                    uv 
                )         
                next_log += 30  # Nächster Log in 30 Sekunden

            time.sleep(2.0)  # Hauptloop alle 2 Sekunden

    except KeyboardInterrupt:
        # Bei Strg+C: Threads und Sensoren sauber beenden
        bme.close()           # Sensor schließen (State speichern)
        ampel.stop()          # Ampel-Thread stoppen
        ampel_thread.join()   # Warten bis Ampel-Thread beendet
        button.stop()         # Button-Thread stoppen
        button.join()         # Warten bis Button-Thread beendet
        pass

if __name__ == "__main__":
    main()
