from gpiozero import PWMOutputDevice  # Importiere Klasse für PWM-Ausgabe (z.B. für Buzzer)
import time  # Importiere Zeitmodul für Pausen

class Buzzer:
    def __init__(self):
        # Initialisiere den Buzzer auf GPIO-Pin 24 als PWM-Ausgang
        # PWM ermöglicht variable Lautstärke durch Pulsweitenmodulation
        self.buzzer = PWMOutputDevice(24)

    def soundsek(self, millisekunden, lautstärke):
        # Gibt für eine bestimmte Zeit einen Ton mit gewünschter Lautstärke aus
        lauts = lautstärke / 100  # Umrechnung von Prozent in Wert zwischen 0.0 und 1.0 (PWM)
        zeit = millisekunden / 1000  # Umrechnung von ms in Sekunden für sleep()
        #print(f"Buzzer an mit {lautstärke:.0f}% Lautstärke")  # Debug-Ausgabe
        self.buzzer.value = lauts  # Setze PWM-Wert (Lautstärke)
        time.sleep(zeit)  # Warte die gewünschte Zeit
        #print("Buzzer aus")  # Debug-Ausgabe
        self.buzzer.off()  # Schalte Buzzer aus (PWM auf 0)

# Testcode
# Buzzer wird im Sekundentakt getestet
# if __name__ == "__main__":
#     buzzer = Buzzer()
#     try:
#         while True:
#             buzzer.soundsek(300, 14)  # 300 ms Ton, 14% Lautstärke
#             time.sleep(1)             # 1 Sekunde Pause
#     except KeyboardInterrupt:
#         print("Test beendet.")
#         buzzer.buzzer.off()           # Buzzer sicher ausschalten


