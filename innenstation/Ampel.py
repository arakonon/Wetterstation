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
        self.running = True

        while self.running and self.alarm.check_acc():   # acc < 2  → True
            self._set_leds([0, 0, 0])   
            sleep(2)                     # 2-s-Takt während Kalibrierung

        if not self.running:             # wurde zwischendurch gestoppt?
            return
        print("[Ampel] Kalibrierung abgeschlossen.")

        while self.running:
            self.alarm.update_values()

            iaq = self.alarm.check_IAQ_quality()
            co2 = self.alarm.check_CO2_quality()
            hum = self.alarm.check_humidity_quality()

            if iaq == 0 or co2 == 0 or hum == 0:
                self._set_leds([0, 1, 0])    # Rot
            elif iaq == 1 or co2 == 1 or hum == 1:
                self._set_leds([0, 0, 1])    # Gelb
            else:
                self._set_leds([1, 0, 0])    # Grün

            sleep(2)                         # 2-s-Takt im Normalbetrieb


    def stop(self):
        """Stoppe die Ampelsteuerung."""
        self.running = False
        self._set_leds([0, 0, 0])  # Alle LEDs aus

    def  ampelt_test(self):
        """Teste die Ampelsteuerung."""
        self._set_leds([1, 0, 0]) #grün
        sleep(1)
        self._set_leds([0, 1, 0]) #rot
        sleep(1)
        self._set_leds([0, 0, 1]) #gelb
        sleep(1)
        self._set_leds([0, 0, 0])

    def _set_leds(self, states):
        """Hilfsfunktion, um die LEDs zu steuern."""
        for led, state in zip(self.leds, states):
            if state:
                led.on()
            else:
                led.off()