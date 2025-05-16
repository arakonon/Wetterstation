from RPLCD.i2c import CharLCD

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

	def display_text(self, line1="", line2=""):
		self.lcd.clear()
		self.lcd.write_string(line1)
		self.lcd.cursor_pos = (1, 0)
		self.lcd.write_string(line2)

	# def cursor(self, zeile, spalte):
	# 	self.lcd.cursor_pos(zeile, spalte)

	

	def display_co2(self):
		self.lcd.create_char(0, self.Carbondioxide_Symbol)
		self.lcd.write_string('\x00') 

	def display_pp(self):
		self.lcd.create_char(1, self.pp_Symbol)
		self.lcd.write_string('\x00') 

		
