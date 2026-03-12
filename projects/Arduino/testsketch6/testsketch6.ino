// Heltec LoRa Node 1 Sketch - OLED disabled, LoRa + relays enabled
// Node 1 of 2: 4 relays + 4 moisture sensors

#include <heltec.h>
#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>

// ------------------ LoRaWAN OTAA KEYS (Node 1) ------------------
static const u1_t PROGMEM APPEUI[8] = { 0xD8, 0xA4, 0x39, 0x12, 0x00, 0x00, 0x00, 0x01 };  // LSB
static const u1_t PROGMEM DEVEUI[8] = { 0x26, 0x01, 0x01, 0xB7, 0x00, 0x00, 0x00, 0xAA };  // LSB
static const u1_t PROGMEM APPKEY[16] = {
  0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
  0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00
};

void os_getArtEui(u1_t *buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui(u1_t *buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey(u1_t *buf) { memcpy_P(buf, APPKEY, 16); }

// ------------------ LMIC Pin Mapping for Heltec WiFi LoRa 32 V3 ------------------
const lmic_pinmap lmic_pins = {
  .nss = 18,
  .rxtx = LMIC_UNUSED_PIN,
  .rst = 14,
  .dio = {26, 35, 34}
};

// ------------------ Relay & Sensor Pins ------------------
const uint8_t relayPins[4] = {16, 17, 21, 22};
const uint8_t resetPins[4] = {4, 5, 12, 13};
const uint8_t moisturePins[4] = {32, 33, 34, 35};

osjob_t sendjob;
const unsigned TX_INTERVAL = 300;  // 5 minutes

void setup() {
  delay(500);
  Serial.begin(115200);
  delay(100);
  //Serial.println("Node 1 Starting - OLED disabled, LoRa enabled");
   Serial.println("STARTING: setup() entered");
  //Heltec.begin(false /*Display*/, true /*LoRa*/, true /*Serial*/);
  Heltec.begin(false, false, true);  // LoRa OFF, OLED OFF, Serial ON
  Serial.println("Heltec.begin completed");

  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    pinMode(resetPins[i], OUTPUT);
    digitalWrite(relayPins[i], LOW);
    digitalWrite(resetPins[i], LOW);
  }

  //os_init();
  //LMIC_reset();
  //LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);
 //LMIC_startJoining();
}

void do_send(osjob_t* j) {
  if (LMIC.opmode & OP_TXRXPEND) {
    Serial.println("LoRa busy");
    return;
  }

  uint8_t data[4];
  for (int i = 0; i < 4; i++) {
    data[i] = analogRead(moisturePins[i]) >> 2;  // Scale to 0-255
  }

  LMIC_setTxData2(1, data, sizeof(data), 0);
  Serial.println("Sending moisture levels...");
}

void onEvent(ev_t ev) {
  switch (ev) {
    case EV_JOINED:
      Serial.println("LoRaWAN Joined!");
      break;

    case EV_TXCOMPLETE:
      Serial.println("LoRa TX Complete");
      if (LMIC.dataLen > 0) {
        Serial.print("Downlink: ");
        for (int i = 0; i < LMIC.dataLen; i++) {
          uint8_t b = LMIC.frame[LMIC.dataBeg + i];
          Serial.print(b, HEX); Serial.print(" ");

          if (i % 2 == 1 && i > 0) {
            uint8_t valve = LMIC.frame[LMIC.dataBeg + i - 1];
            uint8_t cmd = b;
            if (valve >= 1 && valve <= 4) {
              if (cmd == 1) {
                digitalWrite(relayPins[valve - 1], HIGH);
                delay(100);
                digitalWrite(relayPins[valve - 1], LOW);
              } else {
                digitalWrite(resetPins[valve - 1], HIGH);
                delay(100);
                digitalWrite(resetPins[valve - 1], LOW);
              }
            }
          }
        }
        Serial.println();
      }
      os_setTimedCallback(&sendjob, os_getTime() + sec2osticks(TX_INTERVAL), do_send);
      break;

    default:
      break;
  }
}

//void loop() {
 // delay(1000);
 // os_runloop_once();
 void loop() {
  Serial.println("Loop running...");
  delay(2000);
}

