from gpiozero import Button
from signal import pause

button = Button(17, pull_up=True)

# Status merken
gedrueckt = False

def on_press():
    global gedrueckt
    gedrueckt = True
    print("Button gedrückt!")

def on_release():
    global gedrueckt
    if gedrueckt:
        print("Button losgelassen!")
        print("→ Kompletter Tastendruck durchgeführt ✅")
        gedrueckt = False

button.when_pressed = on_press
button.when_released = on_release

print("Warte auf vollständigen Tastendruck...")
pause()
