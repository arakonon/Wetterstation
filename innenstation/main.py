from lcd_control import display_text
from BME680 import BME680Sensor
from Buzzer import Buzzer
from Ampel import Ampel
import time
import threading

bme = BME680Sensor()
buzzer = Buzzer()
ampel = Ampel()

def main():
    # Starte die Ampelsteuerung in einem separaten Thread
    ampel_thread = threading.Thread(target=ampel.start, args=(bme.read_humidity,))
    ampel_thread.start()

    try:
        while True:
            # Ausgabe auf dem LCD
            display_text(f"temp: {bme.read_temperature():.1f}C", f"hum: {bme.read_humidity():.1f}%")
            print("\nTemperatur: %0.1f C" % bme.read_temperature())
            print("Gas: %d ohm" % bme.read_gas())
            print("Luftfeuchtigkeit: %0.1f %%" % bme.read_humidity())
            print("Druck: %0.3f hPa" % bme.read_pressure())
            print("Höhenlage = %0.2f meter" % bme.read_altitude())
            #buzzer.soundsek(500, 10)
            time.sleep(2.0)
    except KeyboardInterrupt:
        # Stoppe die Ampelsteuerung, wenn das Programm beendet wird
        ampel.stop()
        ampel_thread.join()

if __name__ == "__main__":
    main()
