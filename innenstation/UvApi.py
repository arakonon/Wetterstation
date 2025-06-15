import requests
import time

class UvApiClient:
    def __init__(self, bme):
        self.bme = bme
        self.api_key = "API_KEY"  # API-Key für OpenUV
        self.lat = 51.32      # Breitengrad (Standort)
        self.lon = 6.57       # Längengrad
        self.alt = 100        # Höhe (Meter)
        self.lastuv = None  # Letzter gespeicherter UV-Wert
        self.lastupdate = 0 # Zeitpunkt der letzten Abfrage
        self.interval = 1800 # Intervall für neue Abfrage Sekunden, hier 30 Minuten

    def hohleCurrentUv(self):
        now = time.time()  # Aktuelle Zeit holen
        try:
            # Prüfen, ob UV-Wert neu geholt werden muss (noch keiner oder Intervall abgelaufen)
            if self.lastuv is None or now - self.lastupdate > self.interval:
                url = f"https://api.openuv.io/api/v1/uv?lat={self.lat}&lng={self.lon}&alt={self.alt}&dt="  # API-URL bauen
                meinHeader = {
                    "x-access-token": self.api_key  # API-Key im Header übergeben
                }
                response = requests.get(url, headers=meinHeader)  # Anfrage senden
                    # headers= MUSS rein, für die Funktion

                data = response.json()  # Antwort als JSON dekodieren
                self.lastuv = data.get("result", {}).get("uv")  # UV-Wert extrahieren
                    # data ist mein Dictionary, das die Antwort der API enthält 
                    # data.get("result", {}) sucht im Dictionary nach dem Schlüssel "result"
                        # Wenn "result" nicht existiert, kommt das {} zurück 
                    # .get("uv") sucht im "result"-Dictionary nach dem Schlüssel "uv"

                self.lastuv = round(self.lastuv, 1)

                self.lastupdate = now  # Zeitpunkt merken
                    # Wenn API fehler, direkt nochmal?
                    # Also kein Zeit reset

                #self.bme.saveState() # BONUS, halbstündlicher BME kalibr.-Daten Save
                    # Super deplatziert aber funktioniert 
           
        except Exception as fehlerrrrrr:
            print("UV-API Fehler: ", fehlerrrrrr)
            self.lastuv = 404 if self.lastuv is None else self.lastuv  # Falls es direkt fehlschlägt
        
        return self.lastuv  # UV-Wert zurückgeben
