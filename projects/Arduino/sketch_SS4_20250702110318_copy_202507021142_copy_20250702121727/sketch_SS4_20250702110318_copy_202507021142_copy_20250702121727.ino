#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <avr/pgmspace.h>

// Device 3 credentials (replace with your actual keys if needed)
// AppEUI (LSB)
static const u1_t PROGMEM APPEUI[8] = { 0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x05 };
// DevEUI (LSB)
static const u1_t PROGMEM DEVEUI[8] = { 0xDE,0xAD,0xBE,0xEF,0x01,0x02,0x03,0x05 };
// AppKey (MSB)
static const u1_t PROGMEM APPKEY[16] = { 0x2D,0x1F,0x93,0x57,0x42,0x7B,0xA0,0x03,0x2E,0xAE,0x48,0x76,0xF1,0xC2,0x9B,0x05 };

void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

const unsigned TX_INTERVAL = 3600; // seconds

static osjob_t sendjob;

// LoRa pin mapping for generic ATmega328P + RFM95 (Makerfabs-style)
const lmic_pinmap lmic_pins = {
    .nss = 10,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 9,
    .dio = {2, 3, 4},
};

// Helper function to print bytes in hex format
void printHex(const uint8_t* data, uint8_t len) {
    for (uint8_t i = 0; i < len; i++) {
        if (data[i] < 0x10) Serial.print("0");
        Serial.print(data[i], HEX);
        if (i < len - 1) Serial.print(" ");
    }
    Serial.println();
}

void onEvent(ev_t ev) {
    switch(ev) {
        case EV_JOINED:
            Serial.println("Joined TTN.");
            break;
        case EV_TXCOMPLETE:
            Serial.println("TX complete.");
            break;
        default:
            break;
    }
}

void do_send(osjob_t* j){
    uint16_t soil = analogRead(A0);
    int8_t temp = 22;

    Serial.print("Soil raw value: ");
    Serial.println(soil);
    Serial.print("Temperature: ");
    Serial.println(temp);

    uint8_t payload[3];
    payload[0] = soil >> 8;
    payload[1] = soil & 0xFF;
    payload[2] = temp;

    Serial.print("Payload bytes: ");
    printHex(payload, sizeof(payload));  // Print payload bytes for TTN formatter testing

    LMIC_setTxData2(1, payload, sizeof(payload), 0);
    Serial.println("Packet queued");
}

void setup() {
    Serial.begin(4800);  // Use 4800 baud if your board is 8 MHz Pro Mini; otherwise use 9600
    delay(1000);
    Serial.println("Starting Makerfabs Soil Sensor Node - Device 5");

    uint8_t buf[16];
    Serial.print("AppEUI: ");
    os_getArtEui(buf); printHex(buf, 8);

    Serial.print("DevEUI: ");
    os_getDevEui(buf); printHex(buf, 8);

    Serial.print("AppKey: ");
    os_getDevKey(buf); printHex(buf, 16);

    os_init();
    LMIC_reset();
    LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);

    do_send(&sendjob);
}

void loop() {
    os_runloop_once();
}
