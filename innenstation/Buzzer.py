from gpiozero import PWMOutputDevice
import time

class Buzzer:
    def __init__(self):
        # Definiere buzzer als Instanzvariable
        self.buzzer = PWMOutputDevice(24)

    def soundsek(self, millisekunden, lautstärke):
        lauts = lautstärke / 100
        zeit = millisekunden / 1000
        print(f"Buzzer an mit {lautstärke:.0f}% Lautstärke")
        self.buzzer.value = lauts  # Setze die Lautstärke
        time.sleep(zeit)
        print("Buzzer aus")
        self.buzzer.off()

# if __name__ == "__main__":
#     buzzer = Buzzer()
#     try:
#         while True:
#             buzzer.soundsek(300, 14)  # 300 ms, 14% Lautstärke
#             time.sleep(1)             # 1 Sekunde Pause
#     except KeyboardInterrupt:
#         print("Test beendet.")
#         buzzer.buzzer.off()


