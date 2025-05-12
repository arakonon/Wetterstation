from lcd_control import display_text
from BME680 import BME680
from Buzzer import Buzzer
from Ampel import Ampel
import time
import threading

bme = BME680()
buzzer = Buzzer()
ampel = Ampel()

def main():
    # Starte die Ampelsteuerung in einem separaten Thread
    ampel.ampelt_test()  # Teste die Ampelsteuerung
    ampel_thread = threading.Thread(target=ampel.start)
    ampel_thread.start()
    print("warte auf Sensor-Daten")

    try:
        while True:
            # Ausgabe auf dem LCD
            display_text(f"{bme.read_temperature():.1f}C {bme.read_humidity():.1f}%",
                         bme.iaq_str_LCD() + " " + bme.co2_str_LCD())
            print("\nTemperatur: %0.1f C" % bme.read_temperature())
            print("Luftfeuchtigkeit: %0.1f %%" % bme.read_humidity())
            print("Luftqualität:", bme.iaq_str())
            print("CO₂-Äquivalent:", bme.co2_str())

            
            #buzzer.soundsek(500, 10)
            time.sleep(2.0)
    except KeyboardInterrupt:
        bme.close()
        # Stoppe den Buzzer, wenn das Programm beendet wird
        # Stoppe die Ampelsteuerung, wenn das Programm beendet wird
        ampel.stop()
        ampel_thread.join()
        pass

if __name__ == "__main__":
    main()
