import time
import board
import adafruit_bme680

# Erstellen eines Sensorobjekts, das über den Standard-I2C-Bus der Karte kommuniziert
I2C = board.I2C() # verwendet board.SCL und board.SDA
bme680 = adafruit_bme680.Adafruit_BME680_I2C(I2C, debug=False)

# Ändern Sie den Wert so, dass er dem Luftdruck (hPa) auf Meereshöhe entspricht.
bme680.sea_level_pressure = 1013.25

# Normalerweise müssen Sie einen Offset hinzufügen, um die Temperatur des Sensors zu berücksichtigen.
# Dieser Wert liegt in der Regel bei etwa 5 Grad, variiert aber je nach Verwendung.
# Verwenden Sie einen separaten Temperatursensor zur Kalibrierung dieses Sensors.
temperature_offset = -1
while True:
	print("\nTemperatur: %0.1f C" % (bme680.temperature + temperature_offset))
	print("Gas: %d ohm" % bme680.gas)
	print("Luftfeuchtigkeit: %0.1f %%" % bme680.relative_humidity)
	print("Druck: %0.3f hPa" % bme680.pressure)
	print("Höhenlage = %0.2f meter" % bme680.altitude)
	time.sleep(1)
