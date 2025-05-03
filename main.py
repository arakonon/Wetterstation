from lcd_control import display_text
from lcd_control import display_smiley
from  dht22 import  DHT22Reader
import time

sensor = DHT22Reader()
while True:
    temperature_c, humidity = sensor.read()
    if temperature_c is not None and humidity is not None:
        line1 = f"Temp: {temperature_c:.1f}°C"
        line2 = f"Humid: {humidity:.1f}%"
    else:
        line1, line2 = "Fehler beim", "Lesen"

    # Ausgabe auf dem LCD
    display_text(line1, line2)
    # Optional: Smiley anzeigen
    # display_smiley()

    time.sleep(2.0)



#display_text("Wetter:", "23.5C, 60%")
#time.sleep(5)
#display_text("Alles cool!", ":)")
#time.sleep(1)
#display_smiley()
