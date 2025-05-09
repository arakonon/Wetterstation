from gpiozero import LED
from time import sleep

class Ampel:
    def __init__(self):
                
        # Definiere die LEDs
        self.leds = [LED(26), LED(5), LED(6)]
        self.running = False  # Flag, um den Thread zu stoppen?

    def start(self, get_humidity):
        """Starte die Ampelsteuerung basierend auf der Luftfeuchtigkeit."""
        self.running = True
        while self.running:
            humidity = get_humidity()  # Luftfeuchtigkeit abrufen
            if humidity < 35 or humidity > 65:
                self._set_leds([1, 0, 0])  # Rot
            elif 35 <= humidity < 40 or 60 < humidity <= 65:
                self._set_leds([0, 1, 0])  # Gelb
            else:
                self._set_leds([0, 0, 0])  # Grün/aus

            sleep(1)

    def stop(self):
        """Stoppe die Ampelsteuerung."""
        self.running = False
        self._set_leds([0, 0, 0])  # Alle LEDs aus

    def _set_leds(self, states):
        """Hilfsfunktion, um die LEDs zu steuern."""
        for led, state in zip(self.leds, states):
            if state:
                led.on()
            else:
                led.off()