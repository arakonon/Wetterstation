#"Grund"code: https://tutorials-raspberrypi.de/datenaustausch-raspberry-pi-mqtt-broker-client/
import time, threading
import paho.mqtt.client as mqtt


class EspAußen:
    def __init__(self, host = "localhost", topic = "esp32/#", timeout = 600):
        self._host     = host  # Host/IP des MQTT-Brokers speichern
        self._topic    = topic  # Topic-Pattern für ESP32-Daten (alle Subtopics)
        self._timeout  = timeout  # Timeout in Sekunden, wie lange Werte als "frisch" gelten
        self._values   = {}  # Dictionary für empfangene Werte (key: Messgröße, value: (Wert, Zeitstempel))
        self._lock     = threading.Lock()  # Lock für thread-sicheren Zugriff auf Werte

        self._cli = mqtt.Client(  # MQTT-Client initialisieren (Callback-API v1, eindeutige Client-ID)
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id="pi_bridge")
        self._cli.on_connect = self._on_connect  # Callback für Verbindungsaufbau setzen
        self._cli.on_message = self.on_message  # Callback für eingehende Nachrichten setzen
        self._cli.connect(host, 1883, 60)  # Verbindung zum Broker herstellen (Port 1883, Keepalive 60s)
        self._cli.loop_start()  # Netzwerk-Loop im Hintergrund starten

    def _on_connect(self, client, userdata, flags, rc):
        print("[EspAußen] Verbunden, rc", rc)  # Wird aufgerufen, wenn Verbindung zum Broker steht
        client.subscribe(self._topic, qos=1)  # Jetzt auf alle relevanten ESP32-Topics abonnieren (QoS=1)

    def on_message(self, client, userdata, msg):
        print(f"{msg.topic}: {msg.payload.decode()}")  # Topic und Wert ausgeben
        key = msg.topic.split("/")[-1]  # Letzten Teil des Topics als Schlüssel extrahieren (z.B. "temperature")
        try: 
            val = float(msg.payload)  # Payload in float umwandeln
        except ValueError:
            print("[EspAußen] esp werte ungültig")  # Fehler bei ungültigem Wert
            return
        with self._lock:  # Wert und Zeitstempel thread-sicher speichern
            self._values[key] = (val, time.time())

    def get(self, key, default=None):
        with self._lock: 
            val, ts = self._values.get(key, (default, 0))  # Holt aktuellen Wert für key, falls frisch genug, sonst default
        if time.time() - ts < self._timeout:
            return val
        return default  # Wert zu alt oder nicht vorhanden

    def get_str(self, key, fmt="{:.1f}", unit=""):
        val = self.get(key)  # Gibt Wert als formatierten String zurück, sonst "—"
        return "—" if val is None else (fmt.format(val) + unit)

    def age(self, key):
        with self._lock: 
            _, ts = self._values.get(key, (None, 0))  # Gibt das Alter (Sekunden) des letzten Werts für key zurück
        return time.time() - ts

    def is_alive(self):
        with self._lock:
            if not self._values:
                return False  # Prüft, ob in letzter Zeit Werte empfangen wurden (Timeout)
            last_ts = max(ts for _, ts in self._values.values())  # Jüngster Zeitstempel aller Werte
        return time.time() - last_ts < self._timeout

class MQTTPublisher:
    def __init__(self, topic_prefix="wetterstation/innen", host="localhost"):
        self.topic_prefix = topic_prefix  # Prefix für alle Topics (z.B. wetterstation/innen/temp)
        self._cli = mqtt.Client()  # MQTT-Client initialisieren und verbinden
        self._cli.connect(host, 1883, 60)

    def publish(self, values: dict):
        for key, value in values.items():
            topic = f"{self.topic_prefix}/{key}"  # Dictionary mit Messwerten sofort publishen
            try:
                self._cli.publish(topic, value)
                #print(f"[MQTT] {topic}: {value}")  # Debug-Ausgabe
            except Exception as e:
                print(f"[MQTT] Fehler beim Publish: {e}")
