#from lcd_control import LcdControl
from BME680 import BME680
from MqttSubs import EspAußen
#from LegacyCode.Buzzer import Buzzer
from Ampel import Ampel
from Datenbank import Datenbank
import time, os
import threading

bme = BME680(temp_offset=-0.1)
#buzzer = Buzzer()
ampel = Ampel(bme)
#lcd = LcdControl()
speicher = Datenbank()
esp = EspAußen(host="127.0.0.1", timeout=330)

def main():
    # Starte die Ampelsteuerung in einem separaten Thread
    ampel.ampelt_test()  # Teste die Ampelsteuerung
    ampel_thread = threading.Thread(target=ampel.start)
    ampel_thread.start()
    next_log = time.time() + 30 # erster Log nach 30sek
    print("warte auf Sensor-Daten")

    try:
        while True:
            iaq, acc = bme.read_iaq()
            tAußen = esp.get("temperature")
            hAußen = esp.get("humidity")
            tATxt = esp.get_str("temperature", unit="°C")
            hATxt = esp.get_str("humidity"   , unit="% rF")
            
            # # LCD Ausgabe
            # if acc < 2:
            #     lcd.display_calibration(bme.read_temperature(), bme.read_humidity(),
            #                             bme.iaq_str_LCD(), bme.co2_str_LCD())
            # else:
            #     lcd.display_measurement(bme.read_temperature(), bme.read_humidity(),
            #                             bme.iaq_str_LCD(), bme.co2_str_LCD())

            # Terminal Ausgabe    
            os.system('clear')    
            print("\nTemperatur: %0.1f C" % bme.read_temperature())
            print("Luftfeuchtigkeit: %0.1f %%" % bme.read_humidity())
            print("Luftqualität:", bme.iaq_str())
            print("CO₂-Äquivalent:", bme.co2_str())

            if not esp.is_alive():
                print("Außen-Station: connection lost")
            else:
                print(f"\nAußen: Temperatur; {tATxt}  Hum; {hATxt}")
            
            #DatenBank log
            if time.time() >= next_log: # wenn zeit rum log machen         
                speicher.log_row(bme, tAußen, hAußen)         
                next_log += 30             

            
            #buzzer.soundsek(500, 10)
            time.sleep(2.0)
    except KeyboardInterrupt:
        bme.close()
        # Stoppe die Ampelsteuerung, wenn das Programm beendet wird
        ampel.stop()
        ampel_thread.join()
        pass

if __name__ == "__main__":
    main()
