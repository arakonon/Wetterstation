from gpiozero import RGBLED
from time import sleep
from checkQuality import checkQuality
from Buzzer import Buzzer

class Ampel:
    def __init__(self, bmee):
        # Sensor-Objekt speichern (z.B. BME680)
        self.bme = bmee
        # Alarm-Objekt zur Bewertung der Luftqualität erzeugen
        self.alarm = checkQuality(bmee)
        # Buzzer-Objekt für akustische Signale
        self.buzzer = Buzzer()
        # RGB-LED initialisieren (GPIO-Pins: Rot=5, Grün=26, Blau=6)
        self.led = RGBLED(5, 26, 6)
        # Steuerungs-Flag für die Hauptschleife
        self.running = False
        # Zähler für die Ampelphasen (debouncing, um nicht bei jedem schlechten Wert sofort umzuschalten)
        self.rot, self.gelb, self.grün = 3, 3, 3

    def start(self):
        # Ampelsteuerung starten
        self.running = True

        # Kalibrierungsphase: LEDs bleiben aus, solange acc < 2 (Sensor noch nicht bereit)
        while self.running and self.alarm.checkAcc():
            self.led.color = (0, 0, 0)  # LEDs aus
            sleep(2)                    # 2 Sekunden warten

        if not self.running:
            # Falls gestoppt wurde, Funktion verlassen
            return
        print("[Ampel] Kalibrierung abgeschlossen.")

        # Hauptschleife: Ampelsteuerung läuft, solange self.running True ist
        while self.running:
            # Sensorwerte aktualisieren
            self.alarm.updateValues()

            # Einzelne Qualitätswerte abfragen (0=schlecht, 1=mittel, 2=gut)
            iaq = self.alarm.checkIaqQuality()      # Luftqualität
            eco2 = self.alarm.checkEco2Quality()      # eCO2-Gehalt
            hum = self.alarm.checkHumidityQuality() # Luftfeuchtigkeit

            # Wenn einer der Werte schlecht ist (0), Rot-Zähler dekrementieren
            if iaq == 0 or eco2 == 0 or hum == 0:
                self.rot -= 1
                # Wenn Rot-Zähler abgelaufen ist, auf Rot schalten
                if self.rot <= 0:
                    print("[Ampel-Debug] Schalte auf ROT")
                    self.led.color = (0.8, 0, 0)  # Rot mit 80% Helligkeit
                    # Zähler zurücksetzen
                    self.rot, self.gelb, self.grün = 3, 3, 3
                    # Notfallsignal prüfen und ggf. Buzzer aktivieren
                    if self.alarm.checkEmergency():
                        self.buzzer.soundsek(500, 14)

            # Wenn einer der Werte mittel ist (1), Gelb-Zähler dekrementieren
            elif iaq == 1 or eco2 == 1 or hum == 1:
                self.gelb -= 1
                # Wenn Gelb-Zähler abgelaufen ist, auf Gelb schalten
                if self.gelb <= 0:
                    print("[Ampel-Debug] Schalte auf GELB")
                    self.led.color = (0.1, 0.1, 0)  # Gelb mit 10% Helligkeit
                    # Zähler zurücksetzen
                    self.rot, self.gelb, self.grün = 3, 3, 3
            else:
                # Alle Werte gut (2), Grün-Zähler dekrementieren
                self.grün -= 1
                # Wenn Grün-Zähler abgelaufen ist, auf Grün schalten
                if self.grün <= 0:
                    print("[Ampel-Debug] Schalte auf GRÜN")
                    self.led.color = (0, 0.1, 0)  # Grün mit 10% Helligkeit
                    # Zähler zurücksetzen
                    self.rot, self.gelb, self.grün = 3, 3, 3

            # 2 Sekunden warten, bevor nächste Messung erfolgt
            sleep(2)

    def stop(self):
        # Stoppe die Ampelsteuerung
        self.running = False              # Hauptschleife beenden
        self.led.color = (0, 0, 0)       # Alle LEDs ausschalten

    def ampelt_test(self):
        # Teste die Ampelsteuerung
        self.led.color = (0, 0.1, 0)     # Grün einschalten
        sleep(1)
        self.led.color = (0.4, 0.4, 0)   # Gelb einschalten
        sleep(1)
        self.led.color = (0.7, 0, 0)     # Rot einschalten

    # def setLeds(self, states):
    #     # Hilfsfunktion, um die LEDs zu steuern.
    #     # (Wird aktuell nicht verwendet, da RGBLED genutzt wird.)
        
    #     for led, state in zip(self.leds, states):
    #         if state:
    #             led.on()
    #         else:
    #             led.off()