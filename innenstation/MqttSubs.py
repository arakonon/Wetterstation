#"Grund"code: https://tutorials-raspberrypi.de/datenaustausch-raspberry-pi-mqtt-broker-client/
import time, threading
import paho.mqtt.client as mqtt


class EspAußen:
    def __init__(self, host = "localhost", topic = "esp32/#", timeout = 330):
        self._host     = host
        self._topic    = topic
        self._timeout  = timeout
        self._values   = {}              # empfangene Werte gespeichert (z.B. Sensordaten)
        self._lock     = threading.Lock() # Sorgt für thread-sicheren Zugriff auf values (?)

        self._cli = mqtt.Client(                       # gefixt?
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id="pi_bridge")
        self._cli.on_connect = self._on_connect
        self._cli.on_message = self.on_message # Verbindet den Client mit dem MQTT-Broker auf dem angegebenen Host und Port 1883, mit 60 Sekunden Keepalive
        self._cli.connect(host, 1883, 60)
        self._cli.subscribe(topic)
        self._cli.loop_start() 

    def _on_connect(self, client, userdata, flags, rc):
        print("[EspAußen] Verbunden, rc", rc)
        client.subscribe(self._topic)

    def on_message(self, client, userdata, msg):
        print(f"{msg.topic}: {msg.payload.decode()}") # Gibt Topic und Wert aus
        # more callbacks, etc
        key = msg.topic.split("/")[-1] # Extrahiert den letzten Teil des Topics als Schlüssel
        try: 
            val = float(msg.payload) # Wandelt Payload in float um
        except ValueError:
            print("[EspAußen] esp werte ungültig") # Fehlerausgabe bei ungültigem Wert
            return
        with self._lock: # Thread-sicherer Zugriff auf values
            self._values[key] = (val, time.time()) # Speichert Wert und Zeitstempel

    def get(self, key, default=None):
        with self._lock: 
            val, ts = self._values.get(key, (default, 0)) # Wert und Zeitstempel holen
        if time.time() - ts < self._timeout: # Prüfen ob Wert noch aktuell
            return val
        return default                   # zu alt, Default zurück

    def get_str(self, key, fmt="{:.1f}", unit=""):
        val = self.get(key)
        return "—" if val is None else (fmt.format(val) + unit)

    def age(self, key):
        with self._lock: 
            _, ts = self._values.get(key, (None, 0)) # Zeitstempel holen
        return time.time() - ts # Alter berechnen
    
    def is_alive(self):
        with self._lock:
            if not self._values:
                return False
            # jüngster Zeitstempel:
            last_ts = max(ts for _, ts in self._values.values())
        return time.time() - last_ts < self._timeout