#include <Wire.h>
#define I2C_1145 0x60
#define I2C_1151 0x53

void setup() {
  Serial.begin(115200);
  Wire.begin();

  Wire.beginTransmission(I2C_1145);
  Wire.write(0x00);                  // PART_ID-Register
  Wire.endTransmission();
  Wire.requestFrom(I2C_1145, 1);
  if (Wire.available()) {
    Serial.printf("Antwort bei 0x60: 0x%02X (wahrscheinlich SI1145)\n", Wire.read());
  }

  Wire.beginTransmission(I2C_1151);
  Wire.write(0x00);
  Wire.endTransmission();
  Wire.requestFrom(I2C_1151, 1);
  if (Wire.available()) {
    Serial.printf("Antwort bei 0x53: 0x%02X (wahrscheinlich SI1151)\n", Wire.read());
  }
}

  Serial.printf("gar nichts gefunden?");

void loop() {}
