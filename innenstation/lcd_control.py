from RPLCD.i2c import CharLCD

# LCD-Konfiguration – überprüfe deine Adresse mit i2cdetect!
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
              cols=16, rows=2, charmap='A00', auto_linebreaks=True, backlight_enabled=True)

def display_text(line1="", line2=""):
    lcd.clear()
    lcd.write_string(line1)
    lcd.cursor_pos = (1, 0)
    lcd.write_string(line2)

#EmojiTest

smiley = (
	0b00000,
	0b01010,
	0b01010,
	0b00000,
	0b10001,
	0b10001,
	0b01110,
	0b00000,
	)

def display_smiley():
	lcd.create_char(0, smiley)
	lcd.write_string('\x00') 
