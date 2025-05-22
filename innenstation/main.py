from lcd import LcdControl, lcdCheck
from BME680 import BME680
from Mqtt import EspAußen, MQTTPublisher
#from LegacyCode.Buzzer import Buzzer
from Ampel import Ampel
from Datenbank import Datenbank
import time, os
import threading

# Imports, Klasssen
bme = BME680(temp_offset=-0.1)
#buzzer = Buzzer()
ampel = Ampel(bme)
lcd = LcdControl()
button = lcdCheck()  # lcdCheck-Thread-Objekt
speicher = Datenbank()
esp = EspAußen(host="127.0.0.1", timeout=600)
mqtt = MQTTPublisher()

def main():
   
   # Initialisierungszeug
    ampel.ampelt_test()  # Teste die Ampelsteuerung
    ampel_thread = threading.Thread(target=ampel.start)
    ampel_thread.start()
    button.start()  # Starte den lcdCheck-Thread!
    next_log = time.time() + 30 # erster Log nach 30sek
    print("warte auf Sensor-Daten")

    # Main-Loop
    try:
        while True:
            # Werte holen
            iaq, acc = bme.read_iaq()
            tAußen = esp.get("temperature")
            hAußen = esp.get("humidity")
            tATxt = esp.get_str("temperature", unit="°C")
            hATxt = esp.get_str("humidity"   , unit="%rF")
            
            # LCD Ausgabe mit Button Switch
            if button.zustand == 0:
                lcd.lcd.backlight_enabled = True
                if acc < 2:
                    lcd.display_calibration(bme.read_temperature(), bme.read_humidity(),
                                            bme.iaq_str_LCD(), bme.co2_str_LCD())
                else:
                    lcd.display_measurement(bme.read_temperature(), bme.read_humidity(),
                                            bme.iaq_str_LCD(), bme.co2_str_LCD())
            elif button.zustand == 1:
                lcd.lcd.backlight_enabled = True
                if not esp.is_alive():
                    lcd.display_text("Aussenstation:",  "Connection Lost")
                else:
                    lcd.display_text("Aussenstation:", f"{tATxt}  {hATxt}")
            elif button.zustand == 2:
                lcd.lcd.backlight_enabled = False

            # Terminal Ausgabe    
            os.system('clear')    
            print("\nTemperatur: %0.1f °C" % bme.read_temperature())
            print("Luftfeuchtigkeit: %0.1f %%" % bme.read_humidity())
            print("Luftqualität:", bme.iaq_str())
            print("CO₂-Äquivalent:", bme.co2_str())
            if not esp.is_alive():
                print("Außen-Station: connection lost")
            else:
                print(f"\nAußen: Temperatur; {tATxt}  Hum; {hATxt}")

            # Mqtt publish für OpenHab
            werte = {
            "temp": bme.read_temperature(),
            "hum": bme.read_humidity(),
            "iaq": bme.read_iaq()[0],
            "co2": bme.read_co2()[0],
            }
            mqtt.publish(werte)
            
            #DatenBank log
            if time.time() >= next_log: # wenn zeit rum log machen         
                speicher.log_row(bme, tAußen, hAußen)         
                next_log += 30             

            #buzzer.soundsek(500, 10)
            time.sleep(2.0)

    except KeyboardInterrupt:
        # Threads sauber stoppen
        # Warten bis Threads beendet sind
        bme.close()
        ampel.stop()
        ampel_thread.join()
        button.stop()      
        button.join()      
        pass

if __name__ == "__main__":
    main()
