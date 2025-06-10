from RPLCD.i2c import CharLCD
import threading, time
from gpiozero import Button


class LcdControl:

    def __init__(self):
        # LCD initialisieren (I2C-Adresse, 16×2 Zeichen, Zeichensatz, Hintergrundbeleuchtung)
        self.lcd = CharLCD(
            i2c_expander='PCF8574',    # I2C-Port-Expander? auf dem LCD-Modul
            address=0x27,              # I2C-Adresse 
            port=1,                    # I2C-Bus-Nummer auf dem Raspberry Pi (meist Bus 1)
            cols=16,                   # Anzahl der Zeichen pro Zeile (z.B. 16)
            rows=2,                    # Anzahl der Zeilen (z.B. 2)
            charmap='A00',             # Zeichensatz
            auto_linebreaks=True,      # Automatischer Zeilenumbruch am Zeilenende
            backlight_enabled=True     # Hintergrundbeleuchtung direkt anschalten
        )
        
        # Eigene Zeichen als 8x5 Bitmaps(?)(siehe library) definieren (z.B. eCO2, ppm, AI, Sonne etc.)
        # "The HD44780 supports up to 8 user created characters. 
        # A character is defined by a 8x5 bitmap. 
        # The bitmap should be a tuple of 8 numbers, each representing a 5 pixel row. 
        # Each character is written to a specific location in CGRAM (numbers 0-7)." - RPLCD Documentation
        self.Carbondioxide_Symbol = [
            0b00110,
            0b00001,
            0b00010,
            0b00111,
            0b01000,
            0b10100,
            0b10100,
            0b01000
        ]

        self.pp_Symbol = [
            0b11000,
            0b10100,
            0b11000,
            0b10110,
            0b10101,
            0b00110,
            0b00100,
            0b00100
        ]

        self.ai_Symbol = [
            0b01000,
            0b10100,
            0b11101,
            0b10100,
            0b00001,
            0b00001,
            0b00000,
            0b00000
            ]
        
        self.r_Symbol = [
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b11000,
            0b10100,
            0b11000,
            0b10100
            ]
        
        self.sun1_Symbol =[
            0b00000,
            0b10101,
            0b01010,
            0b10001,
            0b01010,
            0b10101,
            0b00000,
            0b00000
            ]

        self.sun2_Symbol = [
            0b00000,
            0b10101,
            0b01010,
            0b10001,
            0b01110,
            0b10101,
            0b00000,
            0b00000
            ]

        self.sun3_Symbol = [
            0b00000,
            0b10101,
            0b01010,
            0b11111,
            0b01110,
            0b10101,
            0b00000,
            0b00000
            ]  

        self.sun4_Symbol = [
            0b00000,
            0b10101,
            0b01110,
            0b11111,
            0b01110,
            0b10101,
            0b00000,
            0b00000
        ]

    def display_text(self, line1="", line2=""):
        # Zeigt zwei Textzeilen auf dem LCD an
        self.lcd.clear()
        self.lcd.write_string(line1)
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(line2)

    def display_eco2(self):
        # eCO2-Symbol auf LCD anzeigen (Char 0)
        self.lcd.create_char(0, self.Carbondioxide_Symbol)
        self.lcd.write_string('\x00') 

    def display_pp(self):
        # ppm-Symbol anzeigen (Char 1)
        self.lcd.create_char(1, self.pp_Symbol)
        self.lcd.write_string('\x01')

    def display_ai(self):
        # AI-Symbol anzeigen (Char 2)
        self.lcd.create_char(2, self.ai_Symbol)
        self.lcd.write_string('\x02') 
    
    def display_r(self):
        # r-Symbol anzeigen (Char 3)
        self.lcd.create_char(3, self.r_Symbol)
        self.lcd.write_string('\x03')

    def display_sun1(self):
        # Sonne-Symbol 1 anzeigen (Char 4)
        self.lcd.create_char(4, self.sun1_Symbol)
        self.lcd.write_string('\x04')

    def display_sun2(self):
        # Sonne-Symbol 2 anzeigen (Char 5)
        self.lcd.create_char(5, self.sun2_Symbol)
        self.lcd.write_string('\x05')

    def display_sun3(self):
        # Sonne-Symbol 3 anzeigen (Char 6)
        self.lcd.create_char(6, self.sun3_Symbol)
        self.lcd.write_string('\x06')

    def display_sun4(self):
        # Sonne-Symbol 4 anzeigen (Char 7)
        self.lcd.create_char(7, self.sun4_Symbol)
        self.lcd.write_string('\x07')

    def display_calibration(self, temperature, humidity, iaq_str, eco2_str):
        # Zeigt Kalibrierungsdaten (Temp, Feuchte, IAQ, eCO2) auf LCD an
        self.display_text(f"{temperature:.1f}°C  {humidity:.1f}%",
                    iaq_str + " " + eco2_str)

    def display_measurement(self, temperature, humidity, iaq_str, eco2_str, eco2):
        # Zeigt Messdaten (Temp, Feuchte, IAQ, eCO2) mit Symbolen auf LCD an
        self.display_text(f" {temperature:.1f}°C  {humidity:.1f}%rF",
                    iaq_str + "      " + eco2_str)
        ppm_placement = 14 if eco2 > 999 else 13 if eco2 > 99 else 12 # Für den Ort, an dem das Symbol "ppm" auf dem LCD angezeigt wird.
            # Für Debug nach "if" auskommentieren, wenn is_plausible fehlschlägt und eco2 zu String wird 


        # Symbole und Einheiten gezielt auf bestimmte Positionen setzen
        self.lcd.cursor_pos = (1, 0)
        self.display_ai()
        self.lcd.cursor_pos = (1, 1)
        self.display_r()
        self.lcd.cursor_pos = (1, 6)
        self.lcd.write_string("e")
        self.lcd.cursor_pos = (1, 7)
        self.lcd.write_string("C")
        self.lcd.cursor_pos = (1, 8)
        self.display_eco2()
        self.lcd.cursor_pos = (1, 9)
        self.lcd.write_string(":")
        self.lcd.cursor_pos = (1, ppm_placement)
        self.display_pp()
        self.lcd.cursor_pos = (1, (ppm_placement + 1))
        self.lcd.write_string("m")
    
    def sunSymbol (self, symbol):
        # Zeigt das passende Sonnen-Symbol je nach Wert an (1-4)
        self.lcd.cursor_pos = (0,15)
        if symbol == 1:
            self.display_sun1()
        elif symbol == 2:
            self.display_sun2()
        elif symbol == 3:
            self.display_sun3()
        elif symbol == 4:
            self.display_sun4()
        # zum Testen von lcd, später ggf. auskommentieren
        # else:
        # 	self.display_sun3()


class lcdCheck(threading.Thread):
    def __init__(self, pin=17, anzahl_zustaende=3, debounce_time=0.6):
        # Initialisiert einen eigenen Thread für die Überwachung des Tasters (Button)
        # pin: GPIO-Pin für den Button
        # anzahl_zustaende: Wie viele Zustände (z.B. Menüpunkte) durchgeschaltet werden können
        # debounce_time: Entprellzeit in Sekunden, um versehentliche Mehrfachauslösung zu verhindern
        
        super().__init__()  # Thread initialisieren
        self._running = True  # Flag, ob der Thread laufen soll
        self.zustand = 0  # Aktueller Zustand (z.B. Menüpunkt)
        self.anzahl_zustaende = anzahl_zustaende  # Maximalzahl der Zustände
        self.button = Button(pin, pull_up=True)  # Button-Objekt mit Pull-Up-Widerstand
        self.debounce_time = debounce_time  # Entprellzeit speichern
        self._last_press = 0  # Zeitpunkt des letzten gültigen Tastendrucks
        self.button.when_pressed = self.naechster_zustand  # Callback für Tastendruck

    def naechster_zustand(self):
        # Wird bei Tastendruck aufgerufen
        # Prüft, ob seit dem letzten Druck genug Zeit vergangen ist (Entprellung)
        now = time.time()
        if now - self._last_press > self.debounce_time:
            # Zustand erhöhen, bei Maximum wieder auf 0 springen
            self.zustand = (self.zustand + 1) % self.anzahl_zustaende
            #print(f"Neuer Zustand: {self.zustand}")  # Debug-Ausgabe
            self._last_press = now  # Zeitpunkt merken

    def run(self):
        # Hauptschleife des Threads, läuft solange self._running True ist
        # Hier könnte man weitere Überwachungsaufgaben einbauen
        while self._running:
            time.sleep(0.1)  # Kurze Pause, um CPU zu schonen

    def stop(self):
        # Setzt das Flag, damit die Thread-Schleife endet
        self._running = False




