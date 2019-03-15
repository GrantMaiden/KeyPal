/*
  LED & CAPACITANCE CONTROL MODULE
*/

 // Use this if you want debug messages
#define DEBUG 1
// Use this to time each request handling
//#define TIMING 1

#ifdef DEBUG
  #define DEBUG_PRINTLN(x) debugSerial.println(x); debugSerial.println()
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
const byte NUM_KEYS = 70;
const byte NUM_CAPS = 8;

const byte LED_OFF = 1;
const byte LED_GREEN = 2;
const byte LED_RED = 3;
const byte LED_ORANGE = 4;

byte leds[NUM_KEYS];

int cap_pins[] = {4, 5};


// Teensy hardware serial. RX: 9, TX: 10
#define debugSerial Serial2

// Global Variables
int ledArray[69];
int count;
int ledsOn = 0; // Number of LEDS that are currently consuming Current

// For the sensor delay
const int numReadings = 5;
int readings[numReadings*8];
int readIndex = 0;
int sensorCount = 0;

// sensor data
int sensorValues[8];

void setup() { 
  int i;
  // Setup the debug serials
  debugSerial.begin(9600);
  DEBUG_PRINTLN("Debugging");
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
  DEBUG_PRINTLN("Connected to client");               

  // TEST CODE FOR LED INITALIAZATION
  /* 
  for(i=0; i<69; i++){
    ledArray[i] = 0;
  }
  ledArray[60] = 1;
  for(i=67; i<69; i++){
    ledArray[i] = 1;
  } 
  for(i=65; i<67; i++){
    ledArray[i] = 2;
  } 
  */
  for(i=0; i<69; i++){
    ledArray[i] = LED_OFF;
  } 
  
  PinSetup(); //Setup Teensy Pins
  //digitalWrite(7, LOW); //Uncomment when using this sketch in PCB version
  for (int thisReading = 0; thisReading < numReadings*8; thisReading++) { // Get Capacitance Sensor Data
    AcquireCapacitance(1);
  }
}

void loop() {
  
  //Output GREEN STATE (1) to shift registers
  GreenState();
  AcquireCapacitance(5600); // Read Capacitance values
  DutyCycleAdjust(); //Duty Cycle Adjustment delay (further testing required -> what is max amperage draw possible from usb?)

  //Output RED STATE (2) to shift registers
  RedState();
  delayMicroseconds(4800); //Duty Cycle Delay For Red State
  DutyCycleAdjust();
  updateSerial();
}

void PinSetup(){
  for (int i = 1; i < 8; i++) {
    pinMode(i, OUTPUT);
  }
}

void AcquireCapacitance (int timer) { // Reads Capacitance from keys. Reads ONE key each time through main program loop. This stops timing issues (capacitance reading takes a long time)
  int deltat = micros();
  
  switch (sensorCount) {
    case 0: 
    readings[readIndex + sensorCount * numReadings] = touchRead(23);
    sensorValues[7] = findMax(sensorCount * numReadings);
    //Serial.println(sensorData1);
    break;
    case 1: 
    readings[readIndex + sensorCount * numReadings] = touchRead(22);
    sensorValues[6] = findMax(sensorCount * numReadings);
    //Serial.println(sensorData2);
    break;
    case 2: 
    readings[readIndex + sensorCount * numReadings] = touchRead(19);
    sensorValues[5] = findMax(sensorCount * numReadings);
    //Serial.println(sensorData3);
    break;
    case 3: 
    readings[readIndex + sensorCount * numReadings] = touchRead(18);
    sensorValues[1] = findMax(sensorCount * numReadings);
    //Serial.println(sensorData4);
    break;
    case 4: 
    readings[readIndex + sensorCount * numReadings] = touchRead(17);
    sensorValues[4] = findMax(sensorCount * numReadings);
    //Serial.println(sensorData5);
    break;
    case 5: 
    readings[readIndex + sensorCount * numReadings] = touchRead(16);
    sensorValues[0] = findMax(sensorCount * numReadings);
    //Serial.println(sensorData6);
    break;
    case 6: 
    readings[readIndex + sensorCount * numReadings] = touchRead(15);
    sensorValues[3] = findMax(sensorCount * numReadings);
    //Serial.println(sensorData7);
    break;
    case 7: 
    readings[readIndex + sensorCount * numReadings] = touchRead(0);
    sensorValues[2] = findMax(sensorCount * numReadings);
    //Serial.println(sensorData8);
    break;
  }
  // advance to the next position in the array:
  if (sensorCount >= 7) {
    readIndex = readIndex + 1;
    sensorCount = 0;
  } else
    sensorCount = sensorCount + 1;

  // if we're at the end of the array...
  if (readIndex >= numReadings) {
    // ...wrap around to the beginning:
    readIndex = 0;
  }

  deltat = micros() - deltat;
  //Serial.println(deltat);
  //Serial.println();
  if (deltat < timer) {
    delayMicroseconds(timer - deltat);
  }
}

int findMax(int startpos) {
  int maxNum = 0;
  int i;
  for (i = startpos; i < startpos + 5; i++) {
    if (readings[i] > maxNum)
      maxNum = readings[i];
  }
  return maxNum;
}

void GreenState(){
  int i;
  digitalWrite(5, HIGH); //Disable Output for Shift registers
  for (i = 0; i<70; i++){
    if (ledArray[i] > 0){ //Count number of LEDS that are ON.
      ledsOn = ledsOn + 1;
    }
    if (ledArray[i] == LED_GREEN || ledArray[i] == LED_ORANGE){
      digitalWrite(2, LOW);
      digitalWrite(3, HIGH);
    }
    else{
      digitalWrite(2, LOW);
      digitalWrite(3, LOW);
    }
    digitalWrite(4, LOW);
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t"); 
    digitalWrite(4, HIGH);
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t");
  }
  digitalWrite(5, LOW); //Enable Output for Shift registers
}

void RedState(){
  int i;
  digitalWrite(5, HIGH); //Disable Output for Shift registers
  for (i = 0; i<70; i++){
    if (ledArray[i] == LED_RED || ledArray[i] == LED_ORANGE){
      digitalWrite(2, HIGH);
      digitalWrite(3, LOW);
      //Serial.write("test");
    }
    else{
      digitalWrite(2, LOW);
      digitalWrite(3, LOW);
    }
    digitalWrite(4, LOW);
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t");
    digitalWrite(4, HIGH);
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t");
  }
  digitalWrite(5, LOW); //Enable Output for Shift registers
}

void DutyCycleAdjust(){ //Decreases the effective duty cycle to prohibit damaging LEDS or drawing to much current.
//    if (ledsOn > 10){
//    digitalWrite(5, HIGH); //Disable Output for Shift registers
//    //delayMicroseconds(ledsOn*10); //Wait After Red State is set
//  }
}


byte res = 0;
int i;
int capValue = 0;
unsigned long stime;

void updateSerial() {
  if (Serial.available() > 0) {
    #ifdef TIMING
      stime = micros();
    #endif
    // Read the next command
    res = Serial.read();
    //DEBUG_PRINTLN("Command code: ");
    //DEBUG_PRINTDEC(res);
    //DEBUG_PRINTLN();
    // Fork logic based on command
    if (res == CMD_LEDS) {
      DEBUG_PRINTLN("Reading key data");
      for (i = 0; i < NUM_KEYS; i = i + 1) {
        ledArray[i] = Serial.read();
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
        DEBUG_PRINTDEC(sensorValues[i]);
        DEBUG_PRINTLN();
        Serial.write(map(sensorValues[i], 0, 65536, 0, 255));
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

