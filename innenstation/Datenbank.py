import csv, datetime
from pathlib import Path

class Datenbank:
    def __init__(self):
        self.LOGFILE = Path("~/Wetterstation/logs/innen.csv").expanduser()

    def log_row(self, sensor):
        ts  = datetime.datetime.now().isoformat(timespec="seconds")
        iaq, _  = sensor.read_iaq()
        co2, _  = sensor.read_co2()
        hum     = sensor.read_humidity()
        temp    = sensor.read_temperature()

        header = ["timestamp", "iaq", "co2_ppm", "hum_rel", "temp_c"]
        new    = [ts, iaq, co2, hum, temp]
        print ("[Datenbank] neue log geschrieben")

        write_header = not self.LOGFILE.exists()
        with open(self.LOGFILE, "a", newline="") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(header)
            w.writerow(new)