from RPLCD.i2c import CharLCD
import threading, time
from gpiozero import Button
from signal import pause

class LcdControl:

	def __init__(self):
		# LCD-Konfiguration
		self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
						   cols=16, rows=2, charmap='A00', auto_linebreaks=True, backlight_enabled=True)
		
		# Eigene Zeichen
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
		self.lcd.clear()
		self.lcd.write_string(line1)
		self.lcd.cursor_pos = (1, 0)
		self.lcd.write_string(line2)

	def display_co2(self):
		self.lcd.create_char(0, self.Carbondioxide_Symbol)
		self.lcd.write_string('\x00') 

	def display_pp(self):
		self.lcd.create_char(1, self.pp_Symbol)
		self.lcd.write_string('\x01')

	def display_ai(self):
		self.lcd.create_char(2, self.ai_Symbol)
		self.lcd.write_string('\x02') 
	
	def display_r(self):
		self.lcd.create_char(3, self.r_Symbol)
		self.lcd.write_string('\x03')

	def display_sun1(self):
		self.lcd.create_char(4, self.sun1_Symbol)
		self.lcd.write_string('\x04')

	def display_sun2(self):
		self.lcd.create_char(5, self.sun2_Symbol)
		self.lcd.write_string('\x05')

	def display_sun3(self):
		self.lcd.create_char(6, self.sun3_Symbol)
		self.lcd.write_string('\x06')

	def display_sun4(self):
		self.lcd.create_char(7, self.sun4_Symbol)
		self.lcd.write_string('\x07')

	def display_calibration(self, temperature, humidity, iaq_str, co2_str):
		self.display_text(f"{temperature:.1f}°C  {humidity:.1f}%",
					iaq_str + " " + co2_str)

	def display_measurement(self, temperature, humidity, iaq_str, co2_str):
		self.display_text(f" {temperature:.1f}°C  {humidity:.1f}%rF",
					iaq_str + "   :" + co2_str + " m")
		
		# self.lcd.cursor_pos = (0, 6)
		# self.display_grad()
		self.lcd.cursor_pos = (1, 0)
		self.display_ai()
		self.lcd.cursor_pos = (1, 1)
		self.display_r()
		self.lcd.cursor_pos = (1, 7)
		self.lcd.write_string("C")
		self.lcd.cursor_pos = (1, 8)
		self.display_co2()
		self.lcd.cursor_pos = (1, 14)
		self.display_pp()
	
	def sunSymbol (self, symbol):
		self.lcd.cursor_pos = (0,14)

		if symbol == 1:
			self.display_sun1()
		elif symbol == 2:
			self.display_sun2()
		elif symbol == 3:
			self.display_sun3()
		elif symbol == 4:
			self.display_sun4()
		
		# zum testen von lcd, später wegkommentieren
		# else:
		# 	self.display_sun3()

	def button_test(self, pin=17):
		button = Button(pin, pull_up=True)
		gedrueckt = False
		tastendruck_fertig = False

		def on_press():
			nonlocal gedrueckt
			gedrueckt = True
			print("Button gedrückt!")

		def on_release():
			nonlocal gedrueckt, tastendruck_fertig
			if gedrueckt:
				print("Button losgelassen!")
				print("→ Kompletter Tastendruck durchgeführt ✅")
				gedrueckt = False
				tastendruck_fertig = True

		button.when_pressed = on_press
		button.when_released = on_release

		print("Warte auf vollständigen Tastendruck...")
		while not tastendruck_fertig:
			time.sleep(0.05)

class lcdCheck(threading.Thread):
	def __init__(self, pin=17, anzahl_zustaende=3, debounce_time=0.6):
		super().__init__()
		self._running = True
		self.zustand = 0
		self.anzahl_zustaende = anzahl_zustaende
		self.button = Button(pin, pull_up=True)
		self.debounce_time = debounce_time
		self._last_press = 0
		self.button.when_pressed = self.naechster_zustand

	def naechster_zustand(self):
		now = time.time()
		if now - self._last_press > self.debounce_time:
			self.zustand = (self.zustand + 1) % self.anzahl_zustaende
			print(f"Neuer Zustand: {self.zustand}")
			self._last_press = now

	def run(self):
		while self._running:
			time.sleep(0.1)

	def stop(self):
		self._running = False




