#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

//Konfiguration
const char* ssid         = "-----";
const char* password     = "-----";
const char* mqtt_server  = "-----";
// final
// ('*' = Zeiger auf ein festes String-Literal im Flash spart RAM)?


#define DHTPIN 4  // #define --> Präprozessor-Makro(?): ersetzt vor der Kompilierung jedes „DHTPIN“ durch „4“, schneller
#define DHTTYPE   DHT22

// UV-Sensor 
#define UV_PIN            34          // ADC1_CH6 = GPIO34


const int    SEND_INTERVAL_MIN = 5;   // ► Mess-/Sende-Intervall
const float  TEMP_OFFSET      = 0.5;  // in °C
const float  HUM_OFFSET       = -1.0; // in %rF

DHT          dht(DHTPIN, DHTTYPE);
WiFiClient   espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  dht.begin();

  // ADC-Setup für UV 
  analogReadResolution(12);                         // Setzt die Auflösung auf 12 Bit → Messwerte von 0–4095 für feinere Abstufung
  analogSetPinAttenuation(UV_PIN, ADC_11db);        // Wählt 11 dB Abschwächung, um am Pin Spannungen korrekt messen zu können
    // Ohne analogSetPinAttenuation(UV_PIN, ADC_11db) bleibt die Standard-Abschwächung (0 dB), 
    // d.h. der ADC misst nur bis 1,1 V; alle höheren Spannungen werden „geclippt“ und führen zu ungenauen (maximalen) Rohwerten?

  // WLAN
  WiFi.begin(ssid, password);
  delay(100);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print('.');
  }
  Serial.println("\nWiFi OK  IP: " + WiFi.localIP().toString());

  // MQTT
  client.setServer(mqtt_server, 1883);
  int attempts = 0;
  const int MAX_ATTEMPTS = 3;
  while (!client.connected() && attempts < MAX_ATTEMPTS) {
    if (client.connect("ESP32Client")) {
      Serial.println("MQTT connected!");
    } else {
      attempts++;
      Serial.printf("MQTT connect fail (%d/%d), retry...\n", attempts, MAX_ATTEMPTS);
        // "(%d/%d)" sind die beiden Platzhalter für ganze Zahlen (signed int). 
        // Beim printf werden sie der Reihe nach durch attempts und MAX_ATTEMPTS ersetzt,
      delay(2000);
    }
  }
  if (!client.connected()) {
    Serial.println("MQTT connect fail, nichts senden & schlafen");
    goSleep();
  }

  // Messung DHT22
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (isnan(t) || isnan(h)) { // Not a Number?
    Serial.println("DHT-Fehler – skip");
  }
  t += TEMP_OFFSET;
  h += HUM_OFFSET;

  char buf[16];                       // Puffer (C-String) mit Platz für bis zu 15 Zeichen + '\0'
  // Für Gleitkommawerte (float) nutzt man dtostrf(), 
  // weil Arduino-Snprintf/Printf standardmäßig keine %f-Ausgabe unterstützt:
  dtostrf(t, 4, 2, buf);              // dtostrf = “double to string float”:  
                                    // wandelt float t in einen C-String um,  
                                    // Gesamtbreite 4 Zeichen, 2 Nachkommastellen, Ergebnis in buf

  client.publish("esp32/temperature", buf, true);
    // buf ist der C-String (Payload), z.B. „23.45“
    // true ist der “retained”-Flag, der Broker speichert die letzte Nachricht 
    // und liefert sie neuen Subscriber sofort nach dem Subscribe aus.
  dtostrf(h,  4, 2, buf);
  client.publish("esp32/humidity",    buf, true);
  Serial.printf("Sent T=%.2f°C  H=%.2f%%\n", t, h);

  // Messung UV-Sensor 
  uint16_t rawUV = analogRead(UV_PIN);  
  // uint16_t ist ein unsigned 16-Bit Ganzzahltyp (0…65535) aus <stdint.h>?
  int kategorie = getSonneKategorie(rawUV);

  // Für ganze Zahlen (uint16_t, int) reicht snprintf() mit "%d" aus:
  snprintf(buf, sizeof(buf), "%d", rawUV);
  client.publish("esp32/sun_raw", buf, true);

  snprintf(buf, sizeof(buf), "%d", kategorie);
  client.publish("esp32/sun_kategorie", buf, true);

  Serial.printf("UV-Rohwert: %4d    Kategorie: %d\n", rawUV, kategorie);
  

  client.disconnect();
  WiFi.disconnect(true, true);

  goSleep();
}

void loop() {
  // never reached
}

// ─── Deep-Sleep Funktion ───────────────────────────────────────────────
void goSleep() {
  const uint64_t SLEEP_US = (uint64_t)SEND_INTERVAL_MIN * 60ULL * 1'000'000ULL;
  Serial.printf("Deep-Sleep %d min …\n", SEND_INTERVAL_MIN);
  esp_sleep_enable_timer_wakeup(SLEEP_US);
  delay(100);
  esp_deep_sleep_start();
}

// Gibt eine von fünf Sonnen-Kategorien als int zurück (0 = nicht sonnig, 4 = super sonnig)
int getSonneKategorie(uint16_t raw) {
  if      (raw <  1) return 0;
  else if (raw <  30) return 1;
  else if (raw < 100) return 2;
  else if (raw < 150) return 3;
  else                return 4;
}
