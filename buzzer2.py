from gpiozero import PWMOutputDevice
import time

buzzer = PWMOutputDevice(24)

try:
    while True:
        print("Buzzer an mit halber Lautstärke")
        buzzer.value = 0.10  # 10 % "Lautstärke"
        time.sleep(4)
        print("Buzzer aus")
        buzzer.off()
        time.sleep(2)
except KeyboardInterrupt:
    print("Test beendet")
