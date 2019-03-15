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

//// Serial Communication Parameters
const byte CMD_LEDS = 1;
const byte CMD_CAPS = 2;
const byte ACK = 64;

//// LED State Parameters
const byte LED_OFF = 1;
const byte LED_GREEN = 2;
const byte LED_RED = 3;
const byte LED_ORANGE = 4;
const byte NUM_KEYS = 70;
byte leds[NUM_KEYS];
// Brightness 
byte led_brightness[NUM_KEYS];
byte brightness_counter = 0;
byte MAX_BRIGHTNESS = 8;

//// Capacitive sensor parameters
const byte NUM_CAPS = 8;
int cap_pins[] = {23, 22, 19, 18, 17, 16, 15, 0};
const byte NUM_READINGS = 5;
// Store the maximum of the most recent readings
int cap_data[NUM_CAPS];
// 2D array to store intermediate reading results
int cap_readings[NUM_CAPS][NUM_READINGS];
int cap_sensor_index = 0;
int cap_reading_index = 0;

// Teensy hardware serial. RX: 0, TX: 1
#define debugSerial Serial1

void setup() {
  // Set LED's initial state
  int i;
  for (i = 0; i < NUM_KEYS; i++) {
    leds[i] = LED_OFF;
    led_brightness[i] = 0;
  }
  for (i = 0; i < MAX_BRIGHTNESS + 1; i++) {
    leds[12 + i] = LED_GREEN;
    led_brightness[12 + i] = i; 
  }
  // Initialize the GPIO pins
  for (i = 1; i < 8; i++) {
    pinMode(i, OUTPUT);
  }
  // Acquire initial sensor readings
  for (i = 0; i < NUM_CAPS * NUM_READINGS; i++) {
    updateSensorData();
  }
  // Setup the debug serial
  debugSerial.begin(9600);
  DEBUG_PRINTLN("Debugging");
  Serial.begin(115200);
}

void loop() {
  // Output Green state to shift registers
  updateLEDState(LED_GREEN);
  // Delay and read next sensor
  beginDelay(700);
  updateSensorData();
  endDelay();
  // Output Red state to shift registers
  updateLEDState(LED_RED);
  // Delay and check for serial communication requests
  beginDelay(600);
  updateSerial();
  endDelay();
  // Increment the brightness counter to control PWM brightness
  brightness_counter++;
  if (brightness_counter >= MAX_BRIGHTNESS) {
    brightness_counter = 0;
  }
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
  cap_readings[cap_sensor_index][cap_reading_index] = touchRead(cap_pins[cap_sensor_index]);
  // Update the data array with the maximum value
  for (int i = 0; i < NUM_READINGS; i++) {
    if (cap_readings[cap_sensor_index][i] > cap_data[cap_sensor_index])
        cap_data[cap_sensor_index] = cap_readings[cap_sensor_index][i];
  }
  // Update the index variables for the next iteration
  cap_reading_index++;
  if (cap_reading_index >= NUM_READINGS) {
    cap_sensor_index = (cap_sensor_index + 1) % NUM_CAPS;
    cap_reading_index = 0;
  }
}

// Updates the shift registers for an LED color based on the given flag
void updateLEDState(byte flag) {
  int i;
  int pin_low, pin_high;
  if (flag == LED_GREEN) {
    pin_low = 2;
    pin_high = 3;
  } else {
    pin_low = 3;
    pin_high = 2;
  }
  digitalWrite(5, HIGH); //Disable Output for Shift registers
  for (i = 0; i < NUM_KEYS; i++){
    if (led_brightness[i] > brightness_counter && (leds[i] == flag || leds[i] == LED_ORANGE)){
      digitalWrite(pin_low, LOW);
      digitalWrite(pin_high, HIGH);
    } else {
      digitalWrite(pin_low, LOW);
      digitalWrite(pin_high, LOW);
    }
    digitalWrite(4, LOW);
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t"); 
    digitalWrite(4, HIGH);
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t");
  }
  digitalWrite(5, LOW); //Enable Output for Shift registers
}

int i;
unsigned long stime;

// Checks serial communication and performs and sending or receiving the client requests
void updateSerial() {
  byte res = 0;
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
      // Update LED array values
      DEBUG_PRINTLN("Reading key data");
      for (i = 0; i < NUM_KEYS; i++) {
        leds[i] = Serial.read();
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
        Serial.write(map(cap_data[i], 0, 1023, 0, 255));
      }
      Serial.write(ACK);
    }
    #ifdef TIMING
      stime = micros() - stime;
      debugSerial.println(stime);
    #endif
  }
}
