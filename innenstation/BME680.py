import time
import board
import adafruit_bme680

class BME680Sensor:
    def __init__(self, temperature_offset=-1):
        # Initialisiere den Sensor
        self.I2C = board.I2C()  # verwendet board.SCL und board.SDA
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(self.I2C, debug=False)
        self.bme680.sea_level_pressure = 1013.25  # Luftdruck auf Meereshöhe
        self.temperature_offset = temperature_offset

    def read_temperature(self):
        return self.bme680.temperature + self.temperature_offset

    def read_gas(self):
        return self.bme680.gas

    def read_humidity(self):
        return self.bme680.relative_humidity

    def read_pressure(self):
        return self.bme680.pressure

    def read_altitude(self):
        return self.bme680.altitude

# sensor = BME680Sensor()

# while True:
#     print("\nTemperatur: %0.1f C" % sensor.read_temperature())
#     print("Gas: %d ohm" % sensor.read_gas())
#     print("Luftfeuchtigkeit: %0.1f %%" % sensor.read_humidity())
#     print("Druck: %0.3f hPa" % sensor.read_pressure())
#     print("Höhenlage = %0.2f meter" % sensor.read_altitude())
#     time.sleep(1)
