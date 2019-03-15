// Use this if you want debug messages
//#define DEBUG 1
// Use this to time each request handling
#define TIMING 1

#ifdef DEBUG
  #define DEBUG_PRINTLN(x) debugSerial.println(x)
  #define DEBUG_PRINT(x) debugSerial.print(x)
  #define DEBUG_PRINTDEC(x) debugSerial.print(x, DEC)
#else
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTDEC(x)
#endif

const byte CMD_LEDS = 1;
const byte CMD_CAPS = 2;
const byte ACK = 64;
const byte NUM_KEYS = 19;
const byte NUM_CAPS = 2;

const byte LED_OFF = 1;
const byte LED_GREEN = 2;
const byte LED_RED = 3;
const byte LED_ORANGE = 4;

byte leds[NUM_KEYS];

int cap_pins[] = {4, 5};
const int ledPin = 13;

// Teensy hardware serial. RX: 0, TX: 1
#define debugSerial Serial1

void setup() {
  int i;
  for (i = 0; i < NUM_KEYS; i = i + 1) {
    leds[i] = LED_OFF;
  }
  // Setup the debug serial
  debugSerial.begin(9600);
  DEBUG_PRINTLN("Debugging");
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
  Serial.write(ACK);
  DEBUG_PRINTLN("Connected to client");
}

byte res = 0;
int i;
int capValue = 0;
unsigned long stime;

void loop() {
  if (Serial.available() > 0) {
    #ifdef TIMING
      stime = micros();
    #endif
    // Read the next command
    res = Serial.read();
    DEBUG_PRINTLN("Command code: ");
    DEBUG_PRINTDEC(res);
    DEBUG_PRINTLN();
    // Fork logic based on command
    if (res == CMD_LEDS) {
      DEBUG_PRINTLN("Reading key data");
      for (i = 0; i < NUM_KEYS; i = i + 1) {
        leds[i] = Serial.read();
      }
      DEBUG_PRINTLN("Done reading key data");
      Serial.write(ACK);
      // Print LED states for debugging
      #ifdef DEBUG
        for (i = 0; i < NUM_KEYS; i = i + 1) {
          DEBUG_PRINTDEC(leds[i]);
          DEBUG_PRINT(' ');
        }
        DEBUG_PRINTLN();
      #endif
    } else if (res == CMD_CAPS) {
      DEBUG_PRINTLN("Sending sensor data");
      Serial.write(NUM_CAPS);
      for (i = 0; i < NUM_CAPS; i = i + 1) {
        capValue = analogRead(cap_pins[i]);
        DEBUG_PRINTDEC(capValue);
        DEBUG_PRINTLN();
        // clamp the sensor value into a byte
        Serial.write(map(capValue, 0, 1023, 0, 255));
      }
      Serial.write(ACK);
    }
    #ifdef TIMING
      stime = micros() - stime;
      debugSerial.println(stime);
    #endif
  }
  //delay(100);
}
