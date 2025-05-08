from lcd_control import display_text
from lcd_control import display_smiley
from  BME680 import BME680Sensor
import time

bme = BME680Sensor()

def main():
    while True:

        # Ausgabe auf dem LCD
        display_text(f"temp: {bme.read_temperature():.1f}C", f"hum: {bme.read_humidity():.1f}%")
        # Optional: Smiley anzeigen
        # display_smiley()

        time.sleep(2.0)

if __name__ == "__main__":
    main()


#display_text("Wetter:", "23.5C, 60%")
#time.sleep(5)
#display_text("Alles cool!", ":)")
#time.sleep(1)
#display_smiley()
