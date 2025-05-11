from gpiozero import LED
from time import sleep
from checkQuality import checkQuality

class Ampel:
    def __init__(self):
        
        self.alarm = checkQuality()  # Instanz der Alarm-Klasse erstellen
        # Definiere die LEDs
        self.leds = [LED(26), LED(5), LED(6)]
        self.running = False  # Flag, um den Thread zu stoppen?

    def start(self):
        """Starte die LED-Ampel (Rot, Gelb, Grün)."""
        self.running = True
        while self.running:
            self.alarm.update_values()  # Sensorwerte aktualisieren

            iaq_status  = self.alarm.check_IAQ_quality()
            co2_status  = self.alarm.check_CO2_quality()
            hum_status  = self.alarm.check_humidity_quality()

            # Gesamtergebnis (Rot dominiert vor Gelb vor Grün)
            if   0 in (iaq_status, co2_status, hum_status):
                self._set_leds([1, 0, 0])   # Rot
            elif 1 in (iaq_status, co2_status, hum_status):
                self._set_leds([0, 1, 0])   # Gelb
            else:
                self._set_leds([0, 0, 1])   # Grün

            sleep(1)   # 1-s-Takt; bei Bedarf anpassen

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