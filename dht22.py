import board
import adafruit_dht

class DHT22Reader:
    """Kapselt das Auslesen des DHT22-Sensors."""
    def __init__(self, pin=board.D23, use_pulseio=False):
        # pigpio-Backend erzwingen, damit es auf Pi 5 und neueren sicher läuft
        self.device = adafruit_dht.DHT22(pin, use_pulseio=use_pulseio)

    def read(self):
        """
        Liest Temperatur und Luftfeuchtigkeit.
        Gibt (temperature_c, humidity) oder (None, None) bei Lesefehler zurück.
        """
        try:
            return self.device.temperature, self.device.humidity
        except RuntimeError:
            return None, None
