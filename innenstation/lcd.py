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
        self.carbondioxideSymbol = [
            0b00110,
            0b00001,
            0b00010,
            0b00111,
            0b01000,
            0b10100,
            0b10100,
            0b01000
        ]

        self.ppSymbol = [
            0b11000,
            0b10100,
            0b11000,
            0b10110,
            0b10101,
            0b00110,
            0b00100,
            0b00100
        ]

        self.aiSymbol = [
            0b01000,
            0b10100,
            0b11101,
            0b10100,
            0b00001,
            0b00001,
            0b00000,
            0b00000
            ]
        
        self.rSymbol = [
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b11000,
            0b10100,
            0b11000,
            0b10100
            ]
        
        self.sun1Symbol =[
            0b00000,
            0b10101,
            0b01010,
            0b10001,
            0b01010,
            0b10101,
            0b00000,
            0b00000
            ]

        self.sun2Symbol = [
            0b00000,
            0b10101,
            0b01010,
            0b10001,
            0b01110,
            0b10101,
            0b00000,
            0b00000
            ]

        self.sun3Symbol = [
            0b00000,
            0b10101,
            0b01010,
            0b11111,
            0b01110,
            0b10101,
            0b00000,
            0b00000
            ]  

        self.sun4Symbol = [
            0b00000,
            0b10101,
            0b01110,
            0b11111,
            0b01110,
            0b10101,
            0b00000,
            0b00000
        ]

    def displayText(self, line1="", line2=""):
        # Zeigt zwei Textzeilen auf dem LCD an
        self.lcd.clear()
        self.lcd.write_string(line1)
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(line2)

    def displayEco2(self):
        # eCO2-Symbol auf LCD anzeigen (Char 0)
        self.lcd.create_char(0, self.carbondioxideSymbol)
        self.lcd.write_string('\x00') 

    def displayPp(self):
        # ppm-Symbol anzeigen (Char 1)
        self.lcd.create_char(1, self.ppSymbol)
        self.lcd.write_string('\x01')

    def displayAi(self):
        # AI-Symbol anzeigen (Char 2)
        self.lcd.create_char(2, self.aiSymbol)
        self.lcd.write_string('\x02') 
    
    def displayR(self):
        # r-Symbol anzeigen (Char 3)
        self.lcd.create_char(3, self.rSymbol)
        self.lcd.write_string('\x03')

    def displaySun1(self):
        # Sonne-Symbol 1 anzeigen (Char 4)
        self.lcd.create_char(4, self.sun1Symbol)
        self.lcd.write_string('\x04')

    def displaySun2(self):
        # Sonne-Symbol 2 anzeigen (Char 5)
        self.lcd.create_char(5, self.sun2Symbol)
        self.lcd.write_string('\x05')

    def displaySun3(self):
        # Sonne-Symbol 3 anzeigen (Char 6)
        self.lcd.create_char(6, self.sun3Symbol)
        self.lcd.write_string('\x06')

    def displaySun4(self):
        # Sonne-Symbol 4 anzeigen (Char 7)
        self.lcd.create_char(7, self.sun4Symbol)
        self.lcd.write_string('\x07')

    def displayCalibration(self, temperature, humidity, iaq_str, eco2_str):
        # Zeigt Kalibrierungsdaten (Temp, Feuchte, IAQ, eCO2) auf LCD an
        self.displayText(f"{temperature:.1f}°C  {humidity:.1f}%",
                    iaq_str + " " + eco2_str)

    def displayMeasurement(self, temperature, humidity, iaq_str, eco2_str, eco2):
        # Zeigt Messdaten (Temp, Feuchte, IAQ, eCO2) mit Symbolen auf LCD an
        self.displayText(f" {temperature:.1f}°C  {humidity:.1f}%rF",
                    iaq_str + "      " + eco2_str)
        ppmPlacement = 14 if eco2 > 999 else 13 if eco2 > 99 else 12 # Für den Ort, an dem das Symbol "ppm" auf dem LCD angezeigt wird.
            # Für Debug nach "if" auskommentieren, wenn isPlausible fehlschlägt und eco2 zu String wird 


        # Symbole und Einheiten gezielt auf bestimmte Positionen setzen
        self.lcd.cursor_pos = (1, 0)
        self.displayAi()
        self.lcd.cursor_pos = (1, 1)
        self.displayR()
        self.lcd.cursor_pos = (1, 6)
        self.lcd.write_string("e")
        self.lcd.cursor_pos = (1, 7)
        self.lcd.write_string("C")
        self.lcd.cursor_pos = (1, 8)
        self.displayEco2()
        self.lcd.cursor_pos = (1, 9)
        self.lcd.write_string(":")
        self.lcd.cursor_pos = (1, ppmPlacement)
        self.displayPp()
        self.lcd.cursor_pos = (1, (ppmPlacement + 1))
        self.lcd.write_string("m")
    
    def sunSymbol(self, symbol):
        # Zeigt das passende Sonnen-Symbol je nach Wert an (1-4)
        self.lcd.cursor_pos = (0,15)
        if symbol == 1:
            self.displaySun1()
        elif symbol == 2:
            self.displaySun2()
        elif symbol == 3:
            self.displaySun3()
        elif symbol == 4:
            self.displaySun4()
        # zum Testen von lcd, später ggf. auskommentieren
        # else:
        # 	self.display_sun3()


class lcdCheck(threading.Thread):
    def __init__(self, pin=17, anzahlZustaende=3, debounceTime=0.6):
        # Initialisiert einen eigenen Thread für die Überwachung des Tasters (Button)
        # pin: GPIO-Pin für den Button
        # anzahl_zustaende: Wie viele Zustände (z.B. Menüpunkte) durchgeschaltet werden können
        # debounce_time: Entprellzeit in Sekunden, um versehentliche Mehrfachauslösung zu verhindern
        
        super().__init__()  # Thread initialisieren
        self.running = True  # Flag, ob der Thread laufen soll
        self.zustand = 0  # Aktueller Zustand (z.B. Menüpunkt)
        self.anzahlZustaende = anzahlZustaende  # Maximalzahl der Zustände
        self.button = Button(pin, pull_up=True)  # Button-Objekt mit Pull-Up-Widerstand
        self.debounceTime = debounceTime  # Entprellzeit speichern
        self.lastPress = 0  # Zeitpunkt des letzten gültigen Tastendrucks
        self.button.when_pressed = self.naechsterZustand  # Callback für Tastendruck

    def naechsterZustand(self):
        # Wird bei Tastendruck aufgerufen
        # Prüft, ob seit dem letzten Druck genug Zeit vergangen ist (Entprellung)
        now = time.time()
        if now - self.lastPress > self.debounceTime:
            # Zustand erhöhen, bei Maximum wieder auf 0 springen
            self.zustand = (self.zustand + 1) % self.anzahlZustaende
            #print(f"Neuer Zustand: {self.zustand}")  # Debug-Ausgabe
            self.lastPress = now  # Zeitpunkt merken

    def run(self):
        # Hauptschleife des Threads, läuft solange self.running True ist
        # Hier könnte man weitere Überwachungsaufgaben einbauen
        while self.running:
            time.sleep(0.1)  # Kurze Pause, um CPU zu schonen

    def stop(self):
        # Setzt das Flag, damit die Thread-Schleife endet
        self.running = False




