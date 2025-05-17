#from BME680 import BME680
#import time

class checkQuality:

    def __init__(self, bmee):
        self.bme = bmee
        #self.mittelTimer = 15

    def update_values(self):
        """Aktualisiere die Sensorwerte."""
        self.iaq, self.iaq_acc = self.bme.read_iaq()
        self.co2, self.co2_acc  = self.bme.read_co2()
        self.hum = self.bme.read_humidity()

        #print(f"[update_values] IAQ {self.iaq:.1f} (Acc {self.iaq_acc})")
        #print(f"[update_values] CO₂ {self.co2:.1f} (Acc {self.co2_acc})")
        #print(f"[update_values] Hum {self.hum:.1f}")

    def update_values_check_acc(self):
        self.iaq, self.iaq_acc = self.bme.read_iaq()
        self.co2, self.co2_acc  = self.bme.read_co2()
        self.hum = self.bme.read_humidity()

        #print("[checkQuality-update_values_check_acc] loop bis acc >= 2")

    def accÜber1(self):
        if self.iaq_acc < 2:
            return True
        else:
            return False


    def check_IAQ_quality(self):
        """Überprüfe die Luftqualität und aktiviere den Alarm bei Bedarf."""
        if self.iaq_acc >= 2:
            #print(f"[check_IAQ_quality] IAQ {self.iaq:.1f} (Acc {self.acc})")
            if self.iaq > 201:  # Lüften
                #print("[check_air_quality] Rot")
                return 0
            elif self.iaq > 120:
                #print("[check_IAQ_quality] Gelb")
                return 1
            else:
                #print("[check_IAQ_quality] Grün")
                return 2
        else:
            print("[check_IAQ_quality] Kalibrierung läuft …")
            return None

    def check_CO2_quality(self):
        """Überprüfe die CO₂-Qualität und aktiviere den Alarm bei Bedarf."""
        if self.co2_acc >= 2:
            #print(f"[check_air_quality] CO₂ {self.co2:.1f} (Acc {self.acc})")
            if self.co2 > 2000:  # Lüften
                #print("[check_CO2_quality] Rot")
                return 0
            elif self.co2 > 1001:
                #print("[check_CO2_quality] Gelb")
                return 1
            else:
                #print("[check_CO2_quality] Grün")
                return 2
        else:
            print("[check_air_quality] Kalibrierung läuft …")
            return None
        
    def check_humidity_quality(self):
        if self.hum > 70:
            #print("[check_humidity_quality] Rot")
            return 0
        elif self.hum > 60:
            #print("[check_humidity_quality] Gelb")
            return 1
        else:
            #print("[check_humidity_quality] Grün")
            return 2
        
    def  check_acc(self):
        checkQuality.update_values_check_acc(self)
        """Überprüfe die Kalibrierung."""
        if self.iaq_acc < 2:
            #print("[check_acc] Kalibrierung läuft …")
            return True
        else:
            print("[check_acc] Kalibrierung abgeschlossen.")
            return False
        


    # def mittel_quality(self):
    #     # Wird jede 2 sec ausgeführt
    #     if self.mittelTimer <= 0:
            
    #     else:
    #         if (self.iaq_acc >= 2):
    #             iaqM = self.iaq
    #             co2M = self.co2
    #             humM = self.hum
    #             self.mittelTimer = self.mittelTimer - 1
    #         else:
    #             print("[checkQuality-mittel_quality] Kalibrierung...")
