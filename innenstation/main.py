#!/usr/bin/env python3

from lcd import LcdControl, lcdCheck
from BME680 import BME680
from Mqtt import EspAußen, MqttPublisher
from Ampel import Ampel
from Datenbank import Datenbank
from UvApi import UvApiClient
from checkQuality import checkQuality
import time
import threading

# Sensor- und Steuerungsobjekte initialisieren
displayAcc = 3 # Standart auf 3, zum testen ohne cal. LCD auf 0
    # acc_wert_lcd standart auf 2, zum testen auf -1
bme = BME680(temp_offset=-0.1,acc_wert_lcd=-1)      # BME680-Sensor mit Temperatur-Offset
ampel = Ampel(bme)                  # Ampel-Logik mit Sensor
lcd = LcdControl()                  # LCD-Anzeige
button = lcdCheck()                 # Thread für Button-Steuerung (Menüumschaltung)
speicher = Datenbank()              # Datenbank/Logger für Mittelwerte
esp = EspAußen(host="127.0.0.1", timeout=900)  # ESP32 Außenstation
mqtt = MqttPublisher()            # MQTT Publisher (für OpenHAB)
uvApi = UvApiClient(bme)               # UV-API-Client für aktuelle UV-Werte
check = checkQuality()              # Hier nur für isPlausible()
def main():
    # Initialisierung und Start aller Threads und Komponenten
    ampel.ampelt_test()  # Teste die Ampelsteuerung (LEDs durchschalten)
    ampelThread = threading.Thread(target=ampel.start)  # Ampel in eigenem Thread starten
    ampelThread.start()
    button.start()  # Button-Thread starten (für Menüumschaltung)
    nextLog = time.time() + 30 # Erster Log nach 30 Sekunden
    wasKalib = False
    # Startzeit merken, um Kalibrierungsdauer zu berechnen
    startT = time.time()
    print("warte auf Sensor-Daten")

    # Haupt-Loop: läuft bis zum Abbruch (Strg+C)
    try:
        while True:
            # Sensorwerte holen (innen & außen)
            iaq, acc = bme.readIaq()  # IAQ-Wert (und Genauigkeit)
            iaq = iaq if check.isPlausible(iaq, 0, 500) else "-"
            print("\n\n[DEBUG] raw iaq, eco2 = " + str(bme.readIaq()) + str(bme.readEco2()))
            
            eco2, eco2Acc = bme.readEco2()
            eco2 = eco2 if check.isPlausible(eco2, 0, 5000) else "-"

            iaqStringLcd = bme.iaqStrLCD()
            iaqStringLcd = iaqStringLcd if iaq != "-" else "---"

            eco2StringLcd = bme.eco2StrLCD()
            eco2StringLcd = eco2StringLcd if eco2 != "-" else "---"
             # ("eco2_string_LCD = bme.eco2StrLCD() if eco2 != "-" else "---""" müsste auch gehen, so wie jetzt gehts halt aber auch)

            tAussen = esp.get("temperature")                # Außentemperatur
            tAussen = tAussen if check.isPlausible(tAussen, -15, 60) else "-" # Plausibel?

            hAussen = esp.get("humidity")                   # Außen rF
            hAussen = hAussen if check.isPlausible(hAussen, 10, 90) else "-" # Plausibel?
            
            tATxt = esp.getStr("temperature", unit="°C") if tAussen != "-" else "---"  # Außentemperatur als String
            hATxt = esp.getStr("humidity", unit="%rF") if hAussen != "-" else "---" # Außenfeuchte als String
            
            sonnenWert = esp.get("sun_raw")                # Sonnenwert (Rohwert)
            sonnenWert = sonnenWert if check.isPlausible(sonnenWert, 0, 4096) else "-"
            
            sonnenKategorie = esp.get("sun_kategorie")     # Sonnenkategorie (1-4)
            sonnenKategorie = sonnenKategorie if sonnenWert != "-" else "-"
            
            uv = uvApi.hohleCurrentUv()                  # UV-Wert von API
            uv = uv if check.isPlausible(uv, 0, 11) else "-"
            
            tempInnen = bme.readTemperature()            # Temperatur innen
            tempInnen = tempInnen if check.isPlausible(tempInnen, 5, 40) else "-" # Plausibel?
            
            humInnen = bme.readHumidity()                  # rF innen
            humInnen = humInnen if check.isPlausible(humInnen, 10, 90) else "-" # Plausibel?

            


            # LCD-Ausgabe je nach Button-Zustand (Menü)
            if button.zustand == 0:
                lcd.lcd.backlight_enabled = True  # Hintergrundbeleuchtung an
                if acc < displayAcc and not wasKalib:
                    mins = int((time.time() - startT) // 60)
                    # Sensor noch nicht kalibriert: Kalibrierungsanzeige
                    lcd.displayCalibration(tempInnen, humInnen, mins) # Für Kalibr. Anzeige unge"plausibilisiert"
                else:
                    wasKalib = True
                    # Sensor kalibriert: Messwerte anzeigen
                    lcd.displayMeasurement(tempInnen, humInnen, iaqStringLcd, eco2StringLcd, eco2, iaq)
                    
            elif button.zustand == 1:
                lcd.lcd.backlight_enabled = True
                if not esp.isAlive():
                    # Außenstation nicht erreichbar
                    lcd.displayText("Aussenstation:",  "Connection Lost")
                else:
                    # Außenwerte und UV anzeigen
                    lcd.displayText(f"Aussen: UV:{uv}", f"{tATxt} {hATxt}")
                    lcd.sunSymbol(sonnenKategorie)  # Sonnen-Symbol je nach Kategorie

            elif button.zustand == 2:
                # Display aus (bisschen Strom sparen)
                lcd.lcd.backlight_enabled = False

            # Terminal-Ausgabe (Debug/Monitoring)
            print("\nTemperatur: %0.1f °C" % tempInnen)
            print("Luftfeuchtigkeit: %0.1f %%" % humInnen)
            print("Luftqualität:", bme.iaqStr())
            print("CO₂-Äquivalent:", bme.eco2Str()) # Plausibilitätsprüfung für Bugfixing weggelassen
            if not esp.isAlive():
                print("Außen-Station: connection lost")
            else:
                print(f"\nAußen: Temperatur; {tATxt}  Hum; {hATxt}")
                print(f"Sun: raw; {sonnenWert} Kategorie {sonnenKategorie}")
                print(f"UV-Wert von API: {uv}")

            # MQTT-Publish für OpenHAB
            if acc > 2:
                 werte = {
                "temp": tempInnen,
                "hum": humInnen,
                "iaq": iaq,
                "eco2": eco2,
                "uvApi": uv,
                }     
            else:
                werte = {
                "temp": tempInnen,
                "hum": humInnen,
                "uvApi": uv,
                }
                # print("\n[DEBUG] Iaq und Eco2 in MQTT nicht gesendet")

            mqtt.publish(werte)
            
            # Datenbank-Logging: alle 30 Sekunden Mittelwerte speichern
            if time.time() >= nextLog:         
                speicher.logRow(
                    bme,
                    tAussen,
                    hAussen,
                    sonnenKategorie,
                    sonnenWert,
                    uv 
                )         
                nextLog += 30  # Nächster Log in 30 Sekunden

            time.sleep(2.0)  # Hauptloop alle 2 Sekunden

    except KeyboardInterrupt:
        # Bei Strg+C: Threads und Sensoren sauber beenden
        bme.close()           # Sensor schließen (State speichern)
        ampel.stop()          # Ampel-Thread stoppen
        ampelThread.join()   # Warten bis Ampel-Thread beendet
        button.stop()         # Button-Thread stoppen
        button.join()         # Warten bis Button-Thread beendet
        pass # Tue nichts?

# Dieser Block sorgt dafür, dass das Programm NUR dann startet, wenn die Datei direkt ausgeführt wird (z.B. mit "python3 main.py").
# Wird die Datei hingegen von einem anderen Python-Skript importiert, passiert hier nichts automatisch.
if __name__ == "__main__":
    main()  # Starte das Hauptprogramm
