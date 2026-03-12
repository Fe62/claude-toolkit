#include <lmic.h>

// After LMIC_reset();


#include <hal/hal.h>
#include <SPI.h>
#include <avr/pgmspace.h>
#include <LowPower.h>
#include <EEPROM.h>

// OTAA credentials
static const u1_t PROGMEM APPEUI[8]  = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x07 };
static const u1_t PROGMEM DEVEUI[8]  = { 0xDE, 0xAD, 0xBE, 0xEF, 0x01, 0x02, 0x03, 0x07 };
static const u1_t PROGMEM APPKEY[16] = { 0x2D, 0x1F, 0x93, 0x57, 0x42, 0x7B, 0xA0, 0x01, 0x2E, 0xAE, 0x48, 0x76, 0xF1, 0xC2, 0x9B, 0x07 };

void os_getArtEui(u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui(u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey(u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

const unsigned TX_INTERVAL = 3600;
static osjob_t sendjob;
bool joined = false;
bool txComplete = false;

const lmic_pinmap lmic_pins = {
  .nss = 10,
  .rxtx = LMIC_UNUSED_PIN,
  .rst = 9,
  .dio = {2, 3, 4},
};


// Define a session struct (manually stored)
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
  Serial.println("Session saved to EEPROM.");
}

bool restoreSession() {
  EEPROM.get(EEPROM_SESSION_ADDR, session);
  if (session.valid != 0x42) {
    Serial.println("No valid session found.");
    return false;
  }
  LMIC.netid = session.netid;
  LMIC.devaddr = session.devaddr;
  memcpy(LMIC.nwkKey, session.nwkKey, 16);
  memcpy(LMIC.artKey, session.artKey, 16);
  LMIC.seqnoUp = session.seqnoUp;
  LMIC.seqnoDn = session.seqnoDn;
  LMIC.opmode &= ~OP_JOINING;
  Serial.println("Session restored from EEPROM.");
  return true;
}

void do_send(osjob_t* j) {
  uint16_t soil = analogRead(A0);
  int8_t temp = 22;

  uint8_t payload[3];
  payload[0] = soil >> 8;
  payload[1] = soil & 0xFF;
  payload[2] = temp;

  Serial.print("Payload: ");
  for (uint8_t i = 0; i < sizeof(payload); i++) {
    Serial.print(payload[i], HEX); Serial.print(" ");
  }
  Serial.println();

  LMIC_setTxData2(1, payload, sizeof(payload), 0);
  Serial.println("Packet queued.");
}

void onEvent(ev_t ev) {
  Serial.print("LMIC Event: "); Serial.println(ev);
  switch (ev) {
    case EV_JOINED:
      Serial.println("Joined TTN!");
      joined = true;
      saveSession();  // save session on first join
      break;
    case EV_TXCOMPLETE:
      Serial.println("TX complete.");
      txComplete = true;
      break;
      case EV_JOIN_FAILED:
      Serial.println("Join failed. Retrying...");
  break;

    default:
      break;
  }
}

void sleepForInterval() {
  Serial.println("Sleeping 1 hour...");
  for (int i = 0; i < 450; i++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }
}

void setup() {
  Serial.begin(9600);
  delay(500);
  Serial.println("\nStarting Soil Sensor Node...");

 os_init();
//LMIC_setPinmap(&lmic_pins); // <-- Add this line!
LMIC_reset();

  LMIC_setClockError(MAX_CLOCK_ERROR * 5 / 100); // 5% error margin
  LMIC_selectSubBand(2); // Use sub-band 1 (channels 8-15)
 // LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);

  if (restoreSession()) {
    joined = true;
    txComplete = true;
  } else {
    Serial.println("Joining via OTAA...");
    LMIC_startJoining();
  }
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
