from BME680 import BME680
import time

class checkQuality:

    def __init__(self):
        self.bme = BME680()

    def update_values(self):
        """Aktualisiere die Sensorwerte."""
        iaq, acc = self.bme.read_iaq()
        co2, acc  = self.bme.read_co2()
        hum = self.bme.read_humidity()

        #print(f"[update_values] IAQ {self.iaq:.1f} (Acc {self.acc})")
        #print(f"[update_values] CO₂ {self.co2:.1f} (Acc {self.acc})")
        #print(f"[update_values] Hum {self.hum:.1f}")



    def check_IAQ_quality(self):
        """Überprüfe die Luftqualität und aktiviere den Alarm bei Bedarf."""
        if self.acc >= 2:
            #print(f"[check_IAQ_quality] IAQ {self.iaq:.1f} (Acc {self.acc})")
            if self.iaq > 150:  # Lüften
                print("[check_air_quality] Rot")
                return 0
            elif self.iaq > 100:
                print("[check_IAQ_quality] Gelb")
                return 1
            else:
                print("[check_IAQ_quality] Grün")
                return 2
        else:
            print("[check_IAQ_quality] Kalibrierung läuft …")
            return None

    def check_CO2_quality(self):
        """Überprüfe die CO₂-Qualität und aktiviere den Alarm bei Bedarf."""
        if self.acc >= 2:
            #print(f"[check_air_quality] CO₂ {self.co2:.1f} (Acc {self.acc})")
            if self.co2 > 1500:  # Lüften
                print("[check_CO2_quality] Rot")
                return 0
            elif self.co2 > 1000:
                print("[check_CO2_quality] Gelb")
                return 1
            else:
                print("[check_CO2_quality] Grün")
                return 2
        else:
            print("[check_air_quality] Kalibrierung läuft …")
            return None
        
    def check_humidity_quality(self):
        if self.hum > 70:
            print("[check_humidity_quality] Rot")
            return 0
        elif self.hum > 60:
            print("[check_humidity_quality] Gelb")
            return 1
        else:
            print("[check_humidity_quality] Grün")
            return 2
        
        