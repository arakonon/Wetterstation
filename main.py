from lcd_control import display_text
from lcd_control import display_smiley
import time

display_text("Wetter:", "23.5C, 60%")
time.sleep(5)
display_text("Alles cool!", ":)")
time.sleep(1)
display_smiley()
