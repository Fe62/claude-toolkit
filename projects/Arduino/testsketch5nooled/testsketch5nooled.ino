#include <heltec.h>

const uint8_t relayPins[4] = {16, 17, 21, 22};

void setup() {
  delay(500);
  Serial.begin(115200);
  delay(100);
  Serial.println("Testing GPIOs without OLED");

  Heltec.begin(false /*Display off*/, false /*LoRa off*/, true /*Serial on*/);

  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], LOW);
  }
}

void loop() {
  for (int i = 0; i < 4; i++) {
    Serial.printf("Relay %d HIGH (GPIO %d)\n", i + 1, relayPins[i]);
    digitalWrite(relayPins[i], HIGH);
    delay(500);
    digitalWrite(relayPins[i], LOW);
    delay(500);
  }
  Serial.println("Cycle done.");
  delay(3000);
}
