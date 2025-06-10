#!/usr/bin/env python3

from lcd import LcdControl, lcdCheck
from BME680 import BME680
from Mqtt import EspAußen, MQTTPublisher
from Ampel import Ampel
from Datenbank import Datenbank
from UvApi import UvApiClient
from checkQuality import checkQuality
import time
import threading

# Sensor- und Steuerungsobjekte initialisieren
bme = BME680(temp_offset=-0.1)      # BME680-Sensor mit Temperatur-Offset
ampel = Ampel(bme)                  # Ampel-Logik mit Sensor
lcd = LcdControl()                  # LCD-Anzeige
button = lcdCheck()                 # Thread für Button-Steuerung (Menüumschaltung)
speicher = Datenbank()              # Datenbank/Logger für Mittelwerte
esp = EspAußen(host="127.0.0.1", timeout=600)  # ESP32 Außenstation
mqtt = MQTTPublisher()              # MQTT Publisher (für OpenHAB)
uvApi = UvApiClient(bme)               # UV-API-Client für aktuelle UV-Werte
check = checkQuality()              # Hier nur für is_plausible()
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
            iaq = iaq if check.is_plausible(iaq, 0, 500) else "-"
            
            eco2, eco2_acc = bme.read_eco2()
            eco2 = eco2 if check.is_plausible(eco2, 0, 5000) else "-"

            iaq_string_LCD = bme.iaq_str_LCD()
            iaq_string_LCD = iaq_string_LCD if iaq != "-" else "---"

            eco2_string_LCD = bme.eco2_str_LCD()
            eco2_string_LCD = eco2_string_LCD if eco2 != "-" else "---"
             # ("eco2_string_LCD = bme.eco2_str_LCD() if eco2 != "-" else "---""" müsste auch gehen, so wie jetzt gehts halt aber auch)

            tAußen = esp.get("temperature")                # Außentemperatur
            tAußen = tAußen if check.is_plausible(tAußen, -15, 60) else "-" # Plausibel?

            hAußen = esp.get("humidity")                   # Außen rF
            hAußen = hAußen if check.is_plausible(hAußen, 10, 90) else "-" # Plausibel?
            
            tATxt = esp.get_str("temperature", unit="°C") if tAußen != "-" else "---"  # Außentemperatur als String
            hATxt = esp.get_str("humidity", unit="%rF") if hAußen != "-" else "---" # Außenfeuchte als String
            
            sonnenWert = esp.get("sun_raw")                # Sonnenwert (Rohwert)
            sonnenWert = sonnenWert if check.is_plausible(sonnenWert, 0, 4096) else "-"
            
            sonnenKategorie = esp.get("sun_kategorie")     # Sonnenkategorie (1-4)
            sonnenKategorie = sonnenKategorie if sonnenWert != "-" else "-"
            
            uv = uvApi.hohle_current_uv()                  # UV-Wert von API
            uv = uv if check.is_plausible(uv, 0, 11) else "-"
            
            temp_innen = bme.read_temperature()            # Temperatur innen
            temp_innen = temp_innen if check.is_plausible(temp_innen, 5, 40) else "-" # Plausibel?
            
            hum_innen = bme.read_humidity()                  # rF innen
            hum_innen = hum_innen if check.is_plausible(hum_innen, 10, 90) else "-" # Plausibel?

            


            # LCD-Ausgabe je nach Button-Zustand (Menü)
            if button.zustand == 0:
                lcd.lcd.backlight_enabled = True  # Hintergrundbeleuchtung an
                if acc < 3:
                    # Sensor noch nicht kalibriert: Kalibrierungsanzeige
                    lcd.display_calibration(temp_innen, hum_innen,
                                            bme.iaq_str_LCD(), bme.eco2_str_LCD()) # Für Kalibr. Anzeige unge"plausibilisiert"
                else:
                    # Sensor kalibriert: Messwerte anzeigen
                    lcd.display_measurement(temp_innen, hum_innen,
                                            iaq_string_LCD, eco2_string_LCD, eco2)
                    
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
            print("\nTemperatur: %0.1f °C" % temp_innen)
            print("Luftfeuchtigkeit: %0.1f %%" % hum_innen)
            print("Luftqualität:", bme.iaq_str())
            print("CO₂-Äquivalent:", bme.eco2_str()) # Plausibilitätsprüfung für Bugfixing weggelassen
            if not esp.is_alive():
                print("Außen-Station: connection lost")
            else:
                print(f"\nAußen: Temperatur; {tATxt}  Hum; {hATxt}")
                print(f"Sun: raw; {sonnenWert} Kategorie {sonnenKategorie}")
                print(f"UV-Wert von API: {uv}")

            # MQTT-Publish für OpenHAB
            werte = {
                "temp": temp_innen,
                "hum": hum_innen,
                "iaq": iaq,
                "eco2": eco2,
                "uvApi": uv,
            }
            mqtt.publish(werte)
            
            # Datenbank-Logging: alle 30 Sekunden Mittelwerte speichern
            if time.time() >= next_log:         
                speicher.logRow(
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
        pass # Tue nichts?

# Dieser Block sorgt dafür, dass das Programm NUR dann startet, wenn die Datei direkt ausgeführt wird (z.B. mit "python3 main.py").
# Wird die Datei hingegen von einem anderen Python-Skript importiert, passiert hier nichts automatisch.
if __name__ == "__main__":
    main()  # Starte das Hauptprogramm
