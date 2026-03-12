#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <avr/pgmspace.h>
#include <LowPower.h>
#include <EEPROM.h>

// OTAA credentials - REPLACE WITH YOUR ACTUAL TTN VALUES
static const u1_t PROGMEM APPEUI[8]  = { 0x07,0x77,0x66,0x55,0x44,0x33, 0x22,0x11,};
static const u1_t PROGMEM DEVEUI[8]  = {0x07,0x03,0x02,0x01,0xEF,0xBE,0xAD,0xDE};
static const u1_t PROGMEM APPKEY[16] = { 0x2D,0x1F,0x93,0x57,0x42,0x7B,0xA0,0x02,0x2E,0xAE,0x48,0x76,0xF1,0xC2,0x9B,0x07 };


void os_getArtEui(u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui(u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey(u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

const unsigned TX_INTERVAL = 3600;
static osjob_t sendjob;
bool joined = false;
bool txComplete = false;

// Pin mapping for your LoRa module - VERIFY THESE PINS FOR YOUR BOARD
const lmic_pinmap lmic_pins = {
  .nss = 10,
  .rxtx = LMIC_UNUSED_PIN,
  .rst = 9,
  .dio = {2, 3, 4},
};

// Session storage struct
struct SessionData {
  uint32_t netid;
  uint32_t devaddr;
  uint8_t nwkKey[16];
  uint8_t artKey[16];
  uint32_t seqnoUp;
  uint32_t seqnoDn;
  uint8_t valid; // must be 0x42 when session is valid
} session;

#define EEPROM_SESSION_ADDR 0

void saveSession() {
  session.netid = LMIC.netid;
  session.devaddr = LMIC.devaddr;
  memcpy(session.nwkKey, LMIC.nwkKey, 16);
  memcpy(session.artKey, LMIC.artKey, 16);
  session.seqnoUp = LMIC.seqnoUp;
  session.seqnoDn = LMIC.seqnoDn;
  session.valid = 0x42;
  EEPROM.put(EEPROM_SESSION_ADDR, session);
  Serial.println(F("Session saved"));
}

bool restoreSession() {
  EEPROM.get(EEPROM_SESSION_ADDR, session);
  if (session.valid != 0x42) {
    Serial.println(F("No session"));
    return false;
  }
  LMIC.netid = session.netid;
  LMIC.devaddr = session.devaddr;
  memcpy(LMIC.nwkKey, session.nwkKey, 16);
  memcpy(LMIC.artKey, session.artKey, 16);
  LMIC.seqnoUp = session.seqnoUp;
  LMIC.seqnoDn = session.seqnoDn;
  LMIC.opmode &= ~OP_JOINING;
  Serial.println(F("Session restored"));
  return true;
}

void do_send(osjob_t* j) {
  if (LMIC.opmode & OP_TXRXPEND) {
    Serial.println(F("Busy"));
    return;
  }
  
  uint16_t soil = analogRead(A0);
  int8_t temp = 22;
  
  uint8_t payload[3];
  payload[0] = soil >> 8;
  payload[1] = soil & 0xFF;
  payload[2] = temp;
  
  Serial.print(F("Soil: ")); Serial.println(soil);
  
  LMIC_setTxData2(1, payload, sizeof(payload), 0);
  Serial.println(F("Queued"));
}

void onEvent(ev_t ev) {
  Serial.print(F("Event: ")); Serial.println(ev);
  switch (ev) {
    case EV_TXCOMPLETE:
      Serial.println(F("TX Complete"));
      if (LMIC.txrxFlags & TXRX_ACK) {
        Serial.println(F("Ack received"));
      }
      if (LMIC.dataLen) {
        Serial.print(F("RX: ")); Serial.println(LMIC.dataLen);
      }
      txComplete = true;
      break;
    case EV_TXSTART:
      Serial.println(F("TX Start"));
      break;
    case EV_JOINING:
      Serial.println(F("Joining"));
      break;
    case EV_JOINED:
      Serial.println(F("Joined!"));
      joined = true;
      saveSession();
      LMIC_setLinkCheckMode(0);
      break;
    case EV_JOIN_FAILED:
      Serial.println(F("Join failed"));
      break;
    case EV_TXCANCELED:
      Serial.println(F("TX Canceled"));
      break;
    case EV_RXCOMPLETE:
      Serial.println(F("RX Complete"));
      break;
    case EV_LINK_DEAD:
      Serial.println(F("Link dead"));
      break;
    case EV_LINK_ALIVE:
      Serial.println(F("Link alive"));
      break;
    default:
      Serial.print(F("Unknown: ")); Serial.println((unsigned) ev);
      break;
  }
}

void sleepForInterval() {
  Serial.println(F("Sleep 1h"));
  Serial.flush();
  for (int i = 0; i < 450; i++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println(F("=== Soil Sensor ==="));
  
  // Initialize LMIC
  os_init();
  LMIC_reset();
  
  // Configure for US915
  LMIC_setClockError(MAX_CLOCK_ERROR * 5 / 100);
  LMIC_selectSubBand(2);
  LMIC_setLinkCheckMode(0);
  LMIC_setDrTxpow(DR_SF7, 14);
  
  Serial.println(F("Starting OTAA join..."));
  LMIC_startJoining();
}

void loop() {
  os_runloop_once();
  
  if (joined && !(LMIC.opmode & OP_TXRXPEND) && txComplete) {
    do_send(&sendjob);
    txComplete = false;
    
    while (LMIC.opmode & OP_TXRXPEND) {
      os_runloop_once();
    }
    
    sleepForInterval();
    txComplete = true;
  }
}