import requests
import time

class UvApiClient:
    def __init__(self):
        # Feste Werte für API-Key und Position
        self.api_key = "openuv-3uu6mrmbfjluxd-io"
        self.lat = 51.32      # Hsnr H-Gebäude
        self.lon = 6.57
        self.alt = 100
        self._last_uv = None
        self._last_update = 0
        self._interval = 1800  # 30 Minuten in Sekunden

    def get_current_uv(self):
        now = time.time()
        if self._last_uv is None or now - self._last_update > self._interval:
            url = f"https://api.openuv.io/api/v1/uv?lat={self.lat}&lng={self.lon}&alt={self.alt}&dt="
            headers = {
                "x-access-token": self.api_key
            }
            response = requests.get(url, headers=headers)
            data = response.json()
            self._last_uv = data.get("result", {}).get("uv")
            self._last_update = now
        return self._last_uv

