/*
  LED & CAPACITANCE CONTROL MODULE
*/
 
// Global Variables
int ledArray[70];
int count;

void setup() {                
  Serial.begin(9600);
  int i;
  for(i=0; i<69; i++){
    ledArray[i] = 0;
  }
  //ledArray[60] = 1;
  for(i=60; i<69; i++){
    ledArray[i] = 1;
  } 
  ledArray[5] = 1;
  PinSetup();
  //digitalWrite(7, LOW); //Uncomment when using this sketch in PCB version
  count = millis();
}

void loop() {
  int i;
  int ledsOn = 0;
  //Check for GREEN STATE (1)
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
  delayMicroseconds(1000); //Wait After Green State is set

  //Duty Cycle Adjustment delay (further testing required -> what is max amperage draw possible from usb?)
  //Currently Expects a max current draw of 200mA
  if (ledsOn > 10){
    digitalWrite(5, HIGH); //Disable Output for Shift registers
    //delayMicroseconds(ledsOn*10); //Wait After Red State is set
  }
  
  
  //Check for RED STATE (2)
  digitalWrite(5, HIGH); //Disable Output for Shift registers
  for (i = 0; i<70; i++){
    Serial.println(ledArray[i]);
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
  delayMicroseconds(1000); //Duty Cycle Delay

  //Duty Cycle Adjustment delay (further testing required -> what is max amperage draw possible from usb?)
  //Currently Expects a max current draw of 200mA
  if (ledsOn > 10){
    digitalWrite(5, HIGH); //Disable Output for Shift registers
    //delayMicroseconds(ledsOn*10);
  }
}

void PinSetup(){
  for (int i = 1; i < 8; i++) {
    pinMode(i, OUTPUT);
  }
}

