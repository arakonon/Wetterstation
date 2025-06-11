#"Grund"code: https://tutorials-raspberrypi.de/datenaustausch-raspberry-pi-mqtt-broker-client/
import time, threading
import paho.mqtt.client as mqtt


class EspAußen:
    def __init__(self, host = "localhost", topic = "esp32/#", timeout = 600):
        self.host     = host  # Host/IP des MQTT-Brokers speichern
            # localhost, weil der Broker auf diesem Pi läuft
        self.topic    = topic  # Topic-Pattern für ESP32-Daten (alle Subtopics)
        self.timeout  = timeout  # Timeout in Sekunden, wie lange Werte als "frisch" gelten
        self.values   = {}  # Dictionary für empfangene Werte (key: Messgröße, value: (Wert, Zeitstempel))
            # Dictionary = HashMap(Java)

        self.cli = mqtt.Client(  # MQTT-Client initialisieren (Callback-API v1, eindeutige Client-ID)
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id="pi_bridge")
        
        self.cli.on_connect = self.onConnect  # Callback für Verbindungsaufbau setzen
        self.cli.on_message = self.onMessage  # Callback für eingehende Nachrichten setzen
            # Callback: „Wenn X passiert, ruf bitte diese Funktion auf.“
            # Die Namen sind vordefinierte Schnittstellen der Bibliothek.
            # Die Bibliothek prüft bei jedem Ereignis, ob eine Funktion in der passenden Variable (on_connect, on_message usw.) gespeichert ist.
            # Wenn ja, wird sie automatisch aufgerufen.

        self.cli.connect(host, 1883, 60)  # Verbindung zum Broker herstellen (Port 1883, Keepalive 60s)
        self.cli.loop_start()  # NETZWERK_LOOP IM HINTERGRUND STARTEN
            # Die Methode loop_start() von paho startet einen eigenen Hintergrund-Thread
            # die: Nachrichten vom MQTT-Broker empfängt; 
            # Nachrichten an den Broker schickt; 
            # und die passenden Callback-Funktionen (wie on_message oder on_connect) aufruft


    def onConnect(self, client, userdata, flags, rc):
        # client: Das MQTT-Client-Objekt selbst; damit kann man z.B. weitere Methoden aufrufen (wie subscribe).
        # userdata: Zusätzliche Benutzerdaten, die man beim Erstellen des Clients angeben kann (meistens None oder nicht genutzt).
        # flags: Ein Dictionary mit Verbindungs-Flags; zeigt z.B. an, ob eine bestehende Session wiederverwendet wird.
        # rc: „Return Code“ – eine Zahl, die angibt, ob die Verbindung erfolgreich war; 0 bedeutet Erfolg, andere Werte zeigen Fehler an.

        print("[EspAussen] Verbunden, rc", rc)  # Wird aufgerufen, wenn Verbindung zum Broker steht
        client.subscribe(self.topic, qos=1)  # Jetzt auf alle relevanten ESP32-Topics abonnieren (QoS=1)

    def onMessage(self, client, userdata, msg):
        print(f"{msg.topic}: {msg.payload.decode()}")  # Topic und Wert ausgeben
        # msg.topic: Das ist der Name des Topics (z.B. esp32/temperature), auf dem die Nachricht empfangen wurde.
        # msg.payload: Das ist der Inhalt (die Daten) der Nachricht – z.B. eine Temperatur wie 23.5.

        key = msg.topic.split("/")[-1]  # Letzten Teil des Topics als Schlüssel extrahieren (z.B. "temperature")
            # .split("/") teilt diesen String an jedem / in eine Liste auf: "esp32/temperature" → ["esp32", "temperature"]
            # [-1] nimmt das letzte Element der Liste, also "temperature" oder "humidity".
        
        try: 
            val = float(msg.payload)  # Payload (Bytes) in float umwandeln
        except ValueError:
            print("[EspAussen] esp werte ungültig")  # Fehler bei ungültigem Wert
            return
        self.values[key] = (val, time.time()) # Speichert Werte mit Key(topic), Wert und Zeit 

    def get(self, key, default=None):
        val, ts = self.values.get(key, (default, 0))  # Holt aktuellen Wert für key, falls frisch genug, sonst default
        if time.time() - ts < self.timeout:
            return val
        return default  # Wert zu alt oder nicht vorhanden

    def getStr(self, key, fmt="{:.1f}", unit=""):
        # fmt ist ein Format-String für Zahlen. Standardwert: "{:.1f}" bedeutet: Eine Nachkommastelle, als Fließkommazahl (z.B. 23.4).
        # z.B. fmt="{:.2f}" für zwei Nachkommastellen.
        # + unit hängt die Einheit an, z.B. "°C" oder "%rF".
        val = self.get(key)  # Gibt Wert als formatierten String zurück, sonst "—"
        return "—" if val is None else (fmt.format(val) + unit)

    def isAlive(self):
        if not self.values: # Wenn leer
            return False  # Prüft, ob in letzter Zeit Werte empfangen wurden (Timeout)
        lastTimestamp = max(timestamp for _, timestamp in self.values.values())  # Jüngster Zeitstempel aller Werte
            # self._values.values() liefert alle gespeicherten Werte, z.B. [(23.5, 1717600000), (45.2, 1717600010)].
            # Jeder Wert ist ein Tupel: (Messwert, Zeitstempel).
            # Der Ausdruck ts for _, ts in ... nimmt nur die Zeitstempel aus allen gespeicherten Werten.
            # max(...) sucht den jüngsten (größten) Zeitstempel heraus, also den Zeitpunkt, an dem zuletzt ein Wert empfangen wurde.
        return time.time() - lastTimestamp < self.timeout

class MqttPublisher:
    def __init__(self, topicPrefix="wetterstation/innen", host="localhost"):
        self.topicPrefix = topicPrefix  # Prefix für alle Topics (z.B. wetterstation/innen/temp)
        self.cli = mqtt.Client()  # MQTT-Client initialisieren und verbinden
        self.cli.connect(host, 1883, 60) # connect ist also eine Methode von paho-mqtt

    def publish(self, values: dict):
        for key, value in values.items(): # Diese Schleife geht für jedes Schlüssel-Wert-Paar im Dictionary einmal durch.
            topic = f"{self.topicPrefix}/{key}"  # Dictionary mit Messwerten sofort publishen
            try:
                self.cli.publish(topic, value)
                #print(f"[MQTT] {topic}: {value}")  # Debug-Ausgabe
            except Exception as e: # Schicke Fehlerausgabe 
                print(f"[MQTT] Fehler beim Publish: {e}")
