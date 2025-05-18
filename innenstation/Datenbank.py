import csv, datetime
from pathlib import Path

class Datenbank:
    def __init__(self):
        self.LOGFILE = Path("~/Wetterstation/logs/innen.csv").expanduser()

    def log_row(self, sensor, tAA, hAA):
        ts  = datetime.datetime.now().isoformat(timespec="seconds")
        iaq, _  = sensor.read_iaq()
        co2, _  = sensor.read_co2()
        hum     = sensor.read_humidity()
        temp    = sensor.read_temperature()
        tA      = tAA
        hA      = hAA

        header = ["timestamp", "iaq", "co2_ppm", "hum_rel", "temp_c", "temp_out", "hum_out"]
        new    = [ts, iaq, co2, hum, temp, tA, hA]
        

        write_header = not self.LOGFILE.exists()
        with open(self.LOGFILE, "a", newline="") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(header)
            w.writerow(new)
            print ("[Datenbank] neue log geschrieben")