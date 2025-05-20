/*********
 Grund­legender Code von Rui Santos
 aber abgeändert (DHT22 + Deep-Sleep alle 5 min)
*********/

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// ---------- Konfiguration ----------
const char* ssid       = "Vodafone-DCF8_2,4Ghz";
const char* password   = "Fmm4b3hMLPUj374h";
const char* mqtt_server = "192.168.0.135";

#define DHTPIN   4
#define DHTTYPE  DHT22
const int    SEND_INTERVAL_MIN = 5;                     // ► Mess-/Sende-Intervall
const float  TEMP_OFFSET = 0.5;     // in 0.5 °C     // optional
const float  HUM_OFFSET  = -1.0;    // in -1 %rF

DHT          dht(DHTPIN, DHTTYPE);
WiFiClient   espClient;
PubSubClient client(espClient);

// ---------- Setup läuft bei jedem Wake ----------
void setup() {
  Serial.begin(115200);
  dht.begin();

  // WLAN
  WiFi.begin(ssid, password);
  delay(100);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(250); Serial.print('.'); }
  Serial.println("\nWiFi OK  IP: " + WiFi.localIP().toString());

  // MQTT
  client.setServer(mqtt_server, 1883);

  // Beispiel für Wiederverbindungslogik:
  int attempts = 0;
  const int MAX_ATTEMPTS = 3;
  while (!client.connected() && attempts < MAX_ATTEMPTS) {
    if (client.connect("ESP32Client")) {
      Serial.println("MQTT connected!");
    } else {
      attempts++;
      Serial.printf("MQTT connect fail (%d/%d), retry...\n", attempts, MAX_ATTEMPTS);
      delay(2000);
    }
  }
  if (!client.connected()) {
    Serial.println("MQTT connect fail → trotzdem senden wir nichts & schlafen");
    goSleep();
  }

  // ---------- Messung ----------
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (isnan(t) || isnan(h)) {
    Serial.println("Sensorfehler – skip");
    goSleep();
  }

  t += TEMP_OFFSET;        // Offset anwenden
  h += HUM_OFFSET;

  char buf[8];
  dtostrf(t, 1, 2, buf);
  client.publish("esp32/temperature", buf, true);
  dtostrf(h, 1, 2, buf);
  client.publish("esp32/humidity", buf, true);

  Serial.printf("Gesendet: %.2f °C  %.2f %%\n", t, h);

  client.disconnect();            // sauber schließen
  WiFi.disconnect(true, true);    // Modem sofort aus

  goSleep();                      // alles erledigtÍ
}

void loop() {}                    // wird nie erreicht

// ---------- Hilfsfunktion: Deep-Sleep ----------
void goSleep() {
  const uint64_t SLEEP_US = (uint64_t)SEND_INTERVAL_MIN * 60ULL * 1'000'000ULL;
  Serial.printf("Deep-Sleep %d min …\n", SEND_INTERVAL_MIN);
  esp_sleep_enable_timer_wakeup(SLEEP_US);
  delay(100);                     // UART flush
  esp_deep_sleep_start();         // Chip aus
}
