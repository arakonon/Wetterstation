import time
import board
import adafruit_dht

# D23 = BCM23, pigpio-Backend erzwingen
dhtDevice = adafruit_dht.DHT22(board.D23, use_pulseio=False)

while True:
    try:
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * 9 / 5 + 32
        humidity      = dhtDevice.humidity
        print(f"Temp: {temperature_f:.1f} F / {temperature_c:.1f} C   Luftfeuchte: {humidity:.1f}%")
    except RuntimeError as e:
        # Lesefehler überspringen
        print(f"Wiederholung nach Fehler: {e}")
    time.sleep(2.0)
