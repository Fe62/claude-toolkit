#include <heltec.h>

// ✅ Relay test pins — safe to use on Heltec LoRa 32 V3
const uint8_t relayPins[4] = {16, 17, 21, 22};

void setup() {
  delay(500);  // Let power stabilize
  Serial.begin(115200);
  Heltec.begin(true /*Display*/, false /*LoRa*/, true /*Serial*/);
  Serial.println("GPIO Relay Pin Test");

  // OLED splash
  Heltec.display->clear();
  Heltec.display->drawString(0, 0, "Relay GPIO Test");
  Heltec.display->display();

  // Initialize relay pins
  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], LOW);
  }
}

void loop() {
  for (int i = 0; i < 4; i++) {
    Serial.printf("Activating Relay %d (GPIO %d)\n", i + 1, relayPins[i]);
    Heltec.display->clear();
    Heltec.display->drawString(0, 0, "Relay " + String(i + 1) + " ON");
    Heltec.display->display();

    digitalWrite(relayPins[i], HIGH);
    delay(500);
    digitalWrite(relayPins[i], LOW);
    delay(500);
  }

  Heltec.display->clear();
  Heltec.display->drawString(0, 0, "Cycle Complete");
  Heltec.display->display();
  delay(3000);  // Wait before repeating
}
