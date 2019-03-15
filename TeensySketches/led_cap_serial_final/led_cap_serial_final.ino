// Use this if you want debug messages
//#define DEBUG 1
// Use this to time each request handling
//#define TIMING 1

#ifdef DEBUG
  #define DEBUG_PRINTLN(x) debugSerial.println(x)
  #define DEBUG_PRINT(x) debugSerial.print(x)
  #define DEBUG_PRINTDEC(x) debugSerial.print(x, DEC)
#else
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTDEC(x)
#endif

#ifdef TIMING
  unsigned long stime;
  #define TIMING_START(msg) stime = micros()
  #define TIMING_STOP() stime = micros() - stime; debugSerial.println(stime)
#else
  #define TIMING_START()
  #define TIMING_STOP()
#endif

const byte CMD_LEDS = 1;
const byte CMD_CAPS = 2;
const byte CMD_INIT = 3;
const byte ACK = 64;

const byte LED_OFF = 1;
const byte LED_GREEN = 2;
const byte LED_RED = 3;
const byte LED_ORANGE = 4;

const byte NUM_KEYS = 70;
byte leds[NUM_KEYS];
int leds_on = 0;

const byte NUM_CAPS = 8;
int cap_pins[] = {15, 18, 0, 16, 17, 19, 22, 23};
// Max value that touch sensor reads
const int DATA_CLAMP_VALUE = 65536;

// Store the maximum of the most recent readings
int cap_data[NUM_CAPS];

// 2D array to store intermediate reading results
int cap_readings[NUM_CAPS];
int cap_sensor_index = 0;

// Teensy hardware serial. RX: 9, TX: 10
#define debugSerial Serial2

//LEDs that are on counter
int ledsOn = 0;

void setup() {
  int i;
  // Set LED's initial state
  for (i = 0; i < NUM_KEYS; i++) {
    leds[i] = LED_OFF;
  }
  // Initialize the GPIO pins
  for (i = 1; i < 8; i++) {
    pinMode(i, OUTPUT);
  }
  for(i=60; i<69; i++){
    leds[i] = 2;
  }
  digitalWrite(7, HIGH); //Uncomment when using this sketch in PCB version
  // Acquire initial sensor readings
  for (i = 0; i < NUM_CAPS; i++) {
    updateSensorData();
  }
  // Setup the debug serial
  debugSerial.begin(9600);
  DEBUG_PRINTLN("Debugging");
  Serial.begin(115200);
}

void loop() {
  // Output Green state to shift registers
  digitalWrite(5, LOW); //Enable Output for Shift registers
  updateLEDState(LED_GREEN);
  // Delay and read next sensor
  beginDelay(5600);
  updateSensorData();
  endDelay();
  DutyCycleAdjust();
  digitalWrite(5, HIGH); //DISABLE Output for Shift registers
  // Delay and check for serial communication requests
  beginDelay(5000);
  updateSerial();
  endDelay();
  DutyCycleAdjust();
}

// Delay tools to allows functions to execute then wait for the remainder of a delay
int delayDelta;
int delayTime;
// Called before the function executes
void beginDelay(int delayMicros) {
  delayTime = delayMicros;
  delayDelta = micros();
}
// Called after to wait for the remaining time, if any
void endDelay() {
  delayDelta = micros() - delayDelta;
  if (delayDelta < delayTime)
    delayMicroseconds(delayTime - delayDelta);
  delayDelta = 0;
  delayTime = 0;
}

// Performs a sensor reading and updates the readings and data arrays
void updateSensorData() {
  // Get the next sensor reading
  cap_data[cap_sensor_index] = touchRead(cap_pins[cap_sensor_index]);
  // Update the index variables for the next iteration
  cap_sensor_index = (cap_sensor_index + 1) % NUM_CAPS;
}

// Updates the shift registers for an LED color based on the given flag
void updateLEDState(byte flag) {
  int i;
  for (i = 0; i < NUM_KEYS; i++){
    if (leds[i] == LED_GREEN){
      digitalWrite(4, HIGH);
      digitalWrite(3, LOW);
    } else {
      digitalWrite(4, LOW);
      digitalWrite(3, LOW);
    }
    digitalWrite(2, LOW);
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t"); 
    digitalWrite(2, HIGH);
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t");
  }
}

// Checks serial communication and performs and sending or receiving the client requests
void updateSerial() {
  int i;
  byte res = 0;
  if (Serial.available() > 0) {
    // Read the next command
    res = Serial.read();
    DEBUG_PRINTLN("Command code: ");
    DEBUG_PRINTDEC(res);
    DEBUG_PRINTLN();
    
    // Fork logic based on command
    if (res == CMD_LEDS) {
      // Update LED array values
      DEBUG_PRINTLN("Reading key data");
      leds_on = 0;
      for (i = 0; i < NUM_KEYS; i++) {
        leds[i] = Serial.read();
        if (leds[i] != LED_OFF)
          leds_on++;
      }
      DEBUG_PRINTLN("Done reading key data");
      Serial.write(ACK);
      
      // Print LED states for debugging
      #ifdef DEBUG
        for (i = 0; i < NUM_KEYS; i++) {
          DEBUG_PRINTDEC(leds[i]);
          DEBUG_PRINT(' ');
        }
        DEBUG_PRINTLN();
      #endif
    } else if (res == CMD_CAPS) {
      // Send sensor data
      DEBUG_PRINTLN("Sending sensor data");
      Serial.write(NUM_CAPS);
      for (i = 0; i < NUM_CAPS; i++) {
        DEBUG_PRINTDEC(cap_data[i]);
        DEBUG_PRINTLN();
        // clamp the sensor value into a byte
        Serial.write(map(cap_data[i], 0, DATA_CLAMP_VALUE, 0, 255));
      }
      Serial.write(ACK);
    } else if (res == CMD_INIT) {
      // Reset LED state and send ACK byte
      for (i = 0; i < NUM_KEYS; i++) {
        leds[i] = LED_OFF;
      }
      Serial.write(ACK);
    }
  }
}

void DutyCycleAdjust(){ //Decreases the effective duty cycle to prohibit damaging LEDS or drawing to much current.
//    if (ledsOn > 10){
//    digitalWrite(5, HIGH); //Disable Output for Shift registers
//    //delayMicroseconds(ledsOn*10); //Wait After Red State is set
//  }
}
