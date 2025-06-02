#include <DHT.h>

// ─── Konfiguration ────────────────────────────────────────────────────
#define DHTPIN       4           // GPIO-Pin fürs DHT22
#define DHTTYPE      DHT22

#define UV_PIN       34          // GPIO34 (ADC1_CH6) fürs UV-Signal

DHT dht(DHTPIN, DHTTYPE);

// Gibt eine von fünf Sonnen-Kategorien als int zurück (0 = nicht sonnig, 4 = super sonnig)
int getSonneKategorie(uint16_t raw) {
  if      (raw <  20) return 0;
  else if (raw <  50) return 1;
  else if (raw < 100) return 2;
  else if (raw < 150) return 3;
  else                return 4;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {}  // warten auf seriellen Port

  // DHT starten
  dht.begin();

  // ADC für UV-Sensor konfigurieren
  analogReadResolution(12);                 // 12-Bit ADC (0–4095)
  analogSetPinAttenuation(UV_PIN, ADC_11db); // Messbereich bis 3.3 V

  Serial.println("=== Sensor Test Start ===");
}

void loop() {
  // ─── DHT22 auslesen ───────────────────────────────────────────────────
  float t = dht.readTemperature();   // Temperatur in °C
  float h = dht.readHumidity();      // Luftfeuchte in % r.F.

  if (isnan(t) || isnan(h)) {
    Serial.println("DHT22-Fehler!");
  } else {
    Serial.printf("DHT22 → T: %.2f °C    H: %.2f %%\n", t, h);
  }

  // ─── UV-Sensor (nur Rohwert und Kategorie) ────────────────────────────
  uint16_t rawUV = analogRead(UV_PIN);
  int kategorie = getSonneKategorie(rawUV);

  Serial.printf("UV-Rohwert: %4d    Kategorie: %d\n", rawUV, kategorie);

  Serial.println("-------------------------------");
  delay(2000);  // alle 2 Sekunden wiederholen
}
