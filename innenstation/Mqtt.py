#"Grund"code: https://tutorials-raspberrypi.de/datenaustausch-raspberry-pi-mqtt-broker-client/
import time, threading
import paho.mqtt.client as mqtt


class EspAußen:
    def __init__(self, host = "localhost", topic = "esp32/#", timeout = 600):
        self._host     = host
        self._topic    = topic
        self._timeout  = timeout
        self._values   = {}
        self._lock     = threading.Lock()

        self._cli = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id="pi_bridge")
        self._cli.on_connect = self._on_connect
        self._cli.on_message = self.on_message
        self._cli.connect(host, 1883, 60)
        # self._cli.subscribe(topic, qos=1)  # <--- Diese Zeile entfernen!
        self._cli.loop_start() 

    def _on_connect(self, client, userdata, flags, rc):
        print("[EspAußen] Verbunden, rc", rc)
        client.subscribe(self._topic, qos=1)  # <--- Hier bleibt qos=1!

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




class MQTTPublisher:
    def __init__(self, topic_prefix="wetterstation/innen", host="localhost"):
        self.topic_prefix = topic_prefix
        self._cli = mqtt.Client()
        self._cli.connect(host, 1883, 60)

    def publish(self, values: dict):
        """Werte sofort publishen"""
        for key, value in values.items():
            topic = f"{self.topic_prefix}/{key}"
            try:
                self._cli.publish(topic, value)
                #print(f"[MQTT] {topic}: {value}")
            except Exception as e:
                print(f"[MQTT] Fehler beim Publish: {e}")
