from BME680 import BME680

bme = BME680()

bme._data()
print(bme.read_temperature())