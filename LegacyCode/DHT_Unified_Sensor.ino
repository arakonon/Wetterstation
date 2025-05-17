#include "DHT.h"

#define DHTPIN 4          // GPIO-Pin, an dem das Signal hängt
#define DHTTYPE DHT22     // DHT 22 (AM2302)

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("Sensorfehler!");
  } else {
    Serial.print("Temperatur: ");
    Serial.print(temp);
    Serial.print(" °C | Luftfeuchtigkeit: ");
    Serial.print(hum);
    Serial.println(" %");
  }

  delay(2000);
}
