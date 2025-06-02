/*********
 Grund­legender Code von Rui Santos
 aber abgeändert (DHT22 + Deep-Sleep alle 5 min)
   + UV-Sensor (GUVA-S12SD) integriert
*********/

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// ---------- Konfiguration ----------
const char* ssid         = "Vodafone-DCF8_2,4Ghz";
const char* password     = "Fmm4b3hMLPUj374h";
const char* mqtt_server  = "192.168.0.135";

#define DHTPIN    4
#define DHTTYPE   DHT22

// UV-Sensor (analoger GUVA-S12SD)
#define UV_PIN            34          // ADC1_CH6 → GPIO34


const int    SEND_INTERVAL_MIN = 5;   // ► Mess-/Sende-Intervall
const float  TEMP_OFFSET      = 0.5;  // in °C
const float  HUM_OFFSET       = -1.0; // in %rF

DHT          dht(DHTPIN, DHTTYPE);
WiFiClient   espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  dht.begin();

  // ─── NEU: ADC-Setup für UV ─────────────────────────────────────────────
  analogReadResolution(12);                         // 12-Bit: 0–4095
  analogSetPinAttenuation(UV_PIN, ADC_11db);        // bis 3.3 V messen
  // ────────────────────────────────────────────────────────────────────

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
      delay(2000);
    }
  }
  if (!client.connected()) {
    Serial.println("MQTT connect fail → nichts senden & schlafen");
    goSleep();
  }

  // ─── Messung DHT22 ───────────────────────────────────────────────────
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (isnan(t) || isnan(h)) {
    Serial.println("DHT-Fehler – skip");
    goSleep();
  }
  t += TEMP_OFFSET;
  h += HUM_OFFSET;

  char buf[16];
  dtostrf(t,  4, 2, buf);
  client.publish("esp32/temperature", buf, true);
  dtostrf(h,  4, 2, buf);
  client.publish("esp32/humidity",    buf, true);
  Serial.printf("Sent T=%.2f°C  H=%.2f%%\n", t, h);

  // ─── Messung UV-Sensor ─────────────────────────────────────────
  uint16_t rawUV = analogRead(UV_PIN);
  int kategorie = getSonneKategorie(rawUV);

  char buf[16];
  snprintf(buf, sizeof(buf), "%d", rawUV);
  client.publish("esp32/sun_raw", buf, true);

  snprintf(buf, sizeof(buf), "%d", kategorie);
  client.publish("esp32/sun_kategorie", buf, true);

  Serial.printf("UV-Rohwert: %4d    Kategorie: %d\n", rawUV, kategorie);
  // ────────────────────────────────────────────────────────────────────

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
  if      (raw <  20) return 0;
  else if (raw <  50) return 1;
  else if (raw < 100) return 2;
  else if (raw < 150) return 3;
  else                return 4;
}
