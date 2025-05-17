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
		
		self.grad_Symbol = [
			0b01000,
			0b10100,
			0b01000,
			0b00000,
			0b00000,
			0b00000,
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

	def display_grad(self):
		self.lcd.create_char(4, self.grad_Symbol)
		self.lcd.write_string('\x04') 

	def display_calibration(self, temperature, humidity, iaq_str, co2_str):
		self.display_text(f"{temperature:.1f}C {humidity:.1f}%",
					iaq_str + " " + co2_str)

	def display_measurement(self, temperature, humidity, iaq_str, co2_str):
		self.display_text(f" {temperature:.1f}C  {humidity:.1f}%rF",
					iaq_str + " C :" + co2_str + " m")
		
		self.lcd.cursor_pos = (0, 6)
		self.display_grad()
		self.lcd.cursor_pos = (1, 0)
		self.display_ai()
		self.lcd.cursor_pos = (1, 1)
		self.display_r()
		self.lcd.cursor_pos = (1, 8)
		self.display_co2()
		self.lcd.cursor_pos = (1, 14)
		self.display_pp()
		

		
