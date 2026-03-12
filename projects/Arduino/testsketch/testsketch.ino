#include <heltec.h>

void setup() {
  delay(1000);
  Serial.begin(115200);
  delay(100);
  Serial.println("Minimal boot test");
  Heltec.begin(true, true, true);
}

void loop() {
  delay(5000);
  Serial.println("Still alive...");
}
