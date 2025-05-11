#from lcd_control import display_text
from BME680 import BME680
from Buzzer import Buzzer
# from Ampel import Ampel
import time
# import threading

bme = BME680()
buzzer = Buzzer()
# ampel = Ampel()

def main():
    # Starte die Ampelsteuerung in einem separaten Thread
    # ampel_thread = threading.Thread(target=ampel.start, args=(bme.read_humidity,))
    # ampel_thread.start()
    print("warte auf Sensor-Daten")

    try:
        while True:
            # Ausgabe auf dem LCD
            #display_text(f"temp: {bme.read_temperature():.1f}C", f"hum: {bme.read_humidity():.1f}%")
            print("\nTemperatur: %0.1f C" % bme.read_temperature())
            
            print("Luftqualität:", bme.iaq_str())
            print("CO₂-Äquivalent:", bme.co2_str())

            
            #buzzer.soundsek(500, 10)
            time.sleep(3.0)
    except KeyboardInterrupt:
        bme.close()
        # Stoppe den Buzzer, wenn das Programm beendet wird
        # Stoppe die Ampelsteuerung, wenn das Programm beendet wird
       #  ampel.stop()
       #  ampel_thread.join()
        pass

if __name__ == "__main__":
    main()
