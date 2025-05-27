from gpiozero import RGBLED
from time import sleep
from checkQuality import checkQuality
from Buzzer import Buzzer

class Ampel:
    def __init__(self, bmee):
        self.bme = bmee
        self.alarm = checkQuality(bmee)      # Instanz der Alarm-Klasse erstellen
        self.buzzer = Buzzer()
        self.led = RGBLED(5, 26, 6)          # Definiere die LEDs
        self.running = False                  # Flag, um den Thread zu stoppen
        self.rot, self.gelb, self.grün = 3, 3, 3

    def start(self):
        self.running = True

        # Kalibrierung: LEDs aus, solange acc < 2
        while self.running and self.alarm.check_acc():
            self.led.color = (0, 0, 0)
            sleep(2)                         # 2-s-Takt während Kalibrierung

        if not self.running:
            return
        print("[Ampel] Kalibrierung abgeschlossen.")

        # Hauptloop: Ampelsteuerung
        while self.running:
            self.alarm.update_values()

            iaq = self.alarm.check_IAQ_quality()
            co2 = self.alarm.check_CO2_quality()
            hum = self.alarm.check_humidity_quality()

            #print(f"[Ampel-Debug] IAQ: {iaq}, CO2: {co2}, HUM: {hum}")
            #print(f"[Ampel-Debug] Zählerstände - Rot: {self.rot}, Gelb: {self.gelb}, Grün: {self.grün}")

            if iaq == 0 or co2 == 0 or hum == 0:
                self.rot -= 1
                #print(f"[Ampel-Debug] Rot-Zähler dekrementiert: {self.rot}")
                if self.rot <= 0:
                    #print("[Ampel-Debug] Schalte auf ROT")
                    self.led.color = (0.8, 0, 0)           # Rot 80%
                    self.rot, self.gelb, self.grün = 3, 3, 3
                    #print("[Ampel-Debug] Zähler zurückgesetzt auf 3")
                    if self.alarm.check_emergency():  # bei Notfallschwellwert Signalton 
                        self.buzzer.soundsek(500, 14)

            elif iaq == 1 or co2 == 1 or hum == 1:
                self.gelb -= 1
                #print(f"[Ampel-Debug] Gelb-Zähler dekrementiert: {self.gelb}")
                if self.gelb <= 0:
                    #print("[Ampel-Debug] Schalte auf GELB")
                    self.led.color = (0.1, 0.1, 0)  # Gelb 10%
                    self.rot, self.gelb, self.grün = 3, 3, 3
                    #print("[Ampel-Debug] Zähler zurückgesetzt auf 3")
            else:
                self.grün -= 1
                #print(f"[Ampel-Debug] Grün-Zähler dekrementiert: {self.grün}")
                if self.grün <= 0:
                    #print("[Ampel-Debug] Schalte auf GRÜN")
                    self.led.color = (0, 0.1, 0)   # Grün 10%
                    self.rot, self.gelb, self.grün = 3, 3, 3
                    #print("[Ampel-Debug] Zähler zurückgesetzt auf 3")

            sleep(2)  # 2-s-Takt im Normalbetrieb

    def stop(self):
        """Stoppe die Ampelsteuerung."""
        self.running = False
        self.led.color = (0, 0, 0)           # Alle LEDs aus

    def ampelt_test(self):
        """Teste die Ampelsteuerung."""
        self.led.color = (0, 0.1, 0)    # Grün
        sleep(1)
        self.led.color = (0.4, 0.4, 0)    # Gelb
        sleep(1)
        self.led.color = (0.7, 0, 0)       # Rot

    def _set_leds(self, states):
        """Hilfsfunktion, um die LEDs zu steuern."""
        for led, state in zip(self.leds, states):
            if state:
                led.on()
            else:
                led.off()