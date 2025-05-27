#include <DHT.h>

// ─── Konfiguration ────────────────────────────────────────────────────
#define DHTPIN       4           // GPIO-Pin fürs DHT22
#define DHTTYPE      DHT22

#define UV_PIN       34          // GPIO34 (ADC1_CH6) fürs UV-Signal

// Sensor-Kennwerte GUVA-S12SD
const float UV_OFFSET_V    = 0.99f;  // Offset-Spannung bei 0 mW/cm²
const float UV_SENSITIVITY = 0.06f;  // V pro (mW/cm²)

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  while(!Serial){}  // warten auf seriellen Port

  // DHT starten
  dht.begin();

  // ADC für UV-Sensor konfigurieren
  analogReadResolution(12);               // 12-Bit ADC (0–4095)
  analogSetPinAttenuation(UV_PIN, ADC_11db);  // Messbereich bis 3.3 V

  Serial.println("=== Sensor Test Start ===");
}

void loop() {
  // ─── DHT22 auslesen ───────────────────────────────────────────────────
  float t = dht.readTemperature();   // Temperatur in °C
  float h = dht.readHumidity();      // Luftfeuchte in %rF

  if (isnan(t) || isnan(h)) {
    Serial.println("DHT22-Fehler!");
  } else {
    Serial.printf("DHT22 → T: %.2f °C    H: %.2f %%\n", t, h);
  }

  // ─── UV-Sensor auslesen ────────────────────────────────────────────────
  uint16_t rawUV = analogRead(UV_PIN);
  float    vAdc  = rawUV * (3.3f / 4095.0f);               // gemessene Spannung
  float    uv    = (vAdc > UV_OFFSET_V)
                   ? (vAdc - UV_OFFSET_V) / UV_SENSITIVITY
                   : 0.0f;                                 // UV in mW/cm²

  Serial.printf("UV    → Raw: %4d    V: %.2f V    UVA: %.2f mW/cm²\n",
                rawUV, vAdc, uv);

  Serial.println("-------------------------------");
  delay(2000);  // alle 2 Sekunden wiederholen
}
