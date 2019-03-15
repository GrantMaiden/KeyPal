/*
  LED & CAPACITANCE CONTROL MODULE
*/
 
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
  Serial.begin(9600);
  int i;

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
    ledArray[i] = 1;
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
  delayMicroseconds(4800); //Duty Cycle Delay For Red State
  DutyCycleAdjust();
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
    if (ledArray[i] == 1 || ledArray[i] == 3){
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
    if (ledArray[i] == 2 || ledArray[i] == 3){
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

