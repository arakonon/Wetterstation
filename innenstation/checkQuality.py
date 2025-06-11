#from BME680 import BME680
#import time
import math

class checkQuality:

    def __init__(self, bmee=None):
        self.bme = bmee  # Sensorobjekt speichern
        #self.mittelTimer = 15  # (Optional) Timer für Mittelwertbildung

    def updateValues(self):
        # Holt aktuelle Messwerte vom Sensor und speichert sie als Attribute
        self.iaq, self.iaq_acc = self.bme.readIaq()      # IAQ-Wert + Genauigkeit
        self.eco2, self.eco2_acc  = self.bme.readEco2()     # eCO2-Wert + Genauigkeit
        self.hum = self.bme.readHumidity()               # Luftfeuchtigkeit
        self.temp = self.bme.readTemperature()           # Temperatur

    def updateValuesCheckAcc(self):
        # Holt nur IAQ-Wert und Genauigkeit (z.B. für Kalibrierungsschleife), einfach so
        self.iaq, self.iaq_acc = self.bme.readIaq()

    def accÜber1(self):
        # True, solange die IAQ-Genauigkeit < 2 ist (Kalibrierung läuft)
        if self.iaq_acc < 2:
            return True
        else:
            return False

    def checkIaqQuality(self):
        # Prüft die Luftqualität anhand des IAQ-Werts (sofern Kalibrierung ok)
        if self.iaq_acc >= 2:
            # IAQ > 151: sehr schlecht (rot), >101: mittel (gelb), sonst gut (grün)
            if self.iaq > 151:
                return 0  # Rot
            elif self.iaq > 101:
                return 1  # Gelb
            else:
                return 2  # Grün
        else:
            #print("[checkIaqQquality] Kalibrierung läuft …")
            return None

    def checkEco2Quality(self):
        # Prüft die eCO2-Qualität (sofern Kalibrierung ok)
        if self.eco2_acc >= 2:
            # eCO2 > 2000: sehr schlecht (rot), >1001: mittel (gelb), sonst gut (grün)
            if self.eco2 > 2000:
                return 0  # Rot
            elif self.eco2 > 1001:
                return 1  # Gelb
            else:
                return 2  # Grün
        else:
            #print("[check_air_quality] Kalibrierung läuft …")
            return None
        
    def checkHumidityQuality(self):
        # Prüft die Luftfeuchtigkeit (ohne Kalibrierung)
        if self.hum > 70:
            return 0  # Rot
        elif self.hum > 60:
            return 1  # Gelb
        else:
            return 2  # Grün
        
    def checkAcc(self):
        # Frische IAQ-Werte holen und prüfen, ob Kalibrierung abgeschlossen ist
        checkQuality.updateValuesCheckAcc(self)
        if self.iaq_acc <= 2:
            # Noch nicht kalibriert
            return True
        else:
            #print("[checkAcc] Kalibrierung abgeschlossen.")
            return False
        
    def checkEmergency(self):
        # Prüft auf Notfallbedingungen (sehr schlechte Werte)
        # eCO2 > 1999, IAQ > 249, Temperatur > 39°C, Luftfeuchte > 79%
        if self.eco2 > 1999 or self.iaq > 249 or self.temp > 39 or self.hum > 79:
            return True
        else:
            return False
        
    def isPlausible(self, value, minVal, maxVal):
        try:
            # Prüft, ob der Wert None ist (also gar kein Wert vorliegt)
            # oder ob der Wert ein float ist UND nan ist.
            # isinstance(value, float): True, wenn value ein float ist
            # math.isnan(value): True, wenn value ein nan ist
            # Das zweite Teilstück wird NUR geprüft wenn value wirklich float
            if value is None or (isinstance(value, float) and math.isnan(value)):
                # Falls einer der beiden Fälle zutrifft, ist der Wert unplausibel
                return False
            # Wenn value kein None und kein NaN ist, prüfe, ob der Wert im erlaubten Bereich liegt
            # minVal <= value <= maxVal: True, wenn value zwischen minVal und maxVal liegt (inklusive)
            return minVal <= value <= maxVal
        except Exception as fehlerrr:
            # Falls beim Vergleich ein Fehler auftritt (z.B. value ist ein String), gib eine Fehlermeldung aus
            print("isPlausible Fehler:", fehlerrr)
            # und gib False zurück, weil der Wert nicht plausibel geprüft werden konnte
            return False


