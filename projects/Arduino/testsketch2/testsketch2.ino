void setup() {
  delay(1000);
  Serial.begin(115200);
  delay(200);
  Serial.println("Boot test OK");
}

void loop() {
  delay(5000);
  Serial.println("Still alive...");
}

