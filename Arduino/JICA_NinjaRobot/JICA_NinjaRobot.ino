#include <SoftwareSerial.h>
#include <Servo.h>
Servo myservo;  // create servo object to control a servo

unsigned long int hum_raw,temp_raw,pres_raw;

// strings from BLE IMBLE comunication
const String Ack_Ok = "OK";
const String Ack_NG = "NG";
const String Conect = "CONECT";
const String Discon = "DISCON";
const String Comand = "00,0000,00:";
const String Send_C = "TXDA ";

// protocol v1 of comunication with BLE
// max of 16 bytes (32 nimbles)
// ID of the reading - 00 ~ 99
// Temperature       - reading digits
// Atm Pression      - reading digits
// Humidity          - reading digits
// PositionX         - position digits
// PositionY         - position digits
// PositionZ         - position digits
int readId = 0;
const int readIdSize = 4;
const int readingSize = 6;
const int positionSize = 2;
// Total: 28 nimbles

// using port 10/11 to receive from BLE, this way
// can use normal serial port for debug
SoftwareSerial portOne(10, 11);

// State of connection with BLE
bool conn = false;

const int PinLED = 8;
int time = 500;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  // initialize serial with BLE at 19200 bauds
  portOne.begin(19200);
  // initialize the BME280 sensor
  setup_BME280();
  pinMode(PinLED, OUTPUT);
  myservo.attach(7);  // attaches the servo on pin 9 to the servo object
  myservo.write(90);
}

// the loop routine runs over and over again forever:
void loop() {
  // Copy of BME loop to read all data from sensors
  double temp_act = 0.0, press_act = 0.0,hum_act=0.0;
  signed long int temp_cal;
  unsigned long int press_cal,hum_cal;
  
  readData();
  
  temp_cal = calibration_T(temp_raw);
  press_cal = calibration_P(pres_raw);
  hum_cal = calibration_H(hum_raw);
  temp_act = (double)temp_cal / 100.0;
  press_act = (double)press_cal / 100.0;
  hum_act = (double)hum_cal / 1024.0;
  
  Serial.print("TEMP : ");
  Serial.print(temp_act);
  Serial.print(" DegC  PRESS : ");
  Serial.print(press_act);
  Serial.print(" hPa  HUM : ");
  Serial.print(hum_act);
  Serial.println(" %"); 
    
  // verify if there is data to receive
  while (portOne.available() > 0) {
    String recv = portOne.readStringUntil('\n');
    
    // if ok or ng, it is an ack from a previous command
    if (recv.startsWith(Ack_Ok) || recv.startsWith(Ack_NG))
      Serial.println ("Ack : " + recv);
    // if starts with the 0s default from IMBLE, it is a command
    else if (recv.startsWith(Comand))
      Serial.println ("Cmd : " + recv);
    // anything else received, just print
    else
      Serial.println("Recv: " + recv);
    
    // update connection status
    if (recv.startsWith(Conect)) conn = true;
    if (recv.startsWith(Discon)) conn = false;
    if (recv.startsWith(Ack_NG)) conn = false;
    
    // treatment of commands
    if (recv.startsWith(Comand))
    {
      // clean the begining of the command
      recv.remove(0, Comand.length());
      recv.replace(",", "");
      int arguments = recv.substring(8).toInt();
      int CmdId = recv.substring(4, 8).toInt();
      switch(CmdId)
      {
        case 1:
          Serial.println("Command1 - LED");
          //int arg1 = arguments.toInt();
          if (arguments > 0) time = arguments;
          Serial.println("LED Blink -> " + String(time));
          break;
          
        case 2:
          Serial.println("Command2 - Servo");
          //int arg2 = arguments.toInt();
          switch (arguments)
          {
            case 0:
              Serial.println("Servo: Center");
              myservo.write(90);
              break;
            case 1:
              Serial.println("Servo: Left");
              myservo.write(0);
              break;
            case 2:
              Serial.println("Servo: Right");
              myservo.write(180);
              break;
          }
          break;
      }
    }
  }

  // treatment when the connection is open
  if (conn)
  {
    // Send the reading measures to the BLE
    String data = mount_protocol_v1(temp_cal, press_cal, hum_cal, 99, 55, 33);
    
    // Send data
    Serial.println("Send: " + data);
    portOne.println(Send_C + data);
  }
  
  cmdBlink(time);
}

// function to mount the message to be sent, using protocol v1
String mount_protocol_v1(signed long int temp, unsigned long int pression, unsigned long int hum,
                      int x, int y, int z)
{
  readId = readId + 1 < pow(10,readIdSize) ? readId + 1 : 0;  
  
  return convInt2StringFixedSize(readId  , readIdSize)   +
         convInt2StringFixedSize(temp    , readingSize)  +
         convInt2StringFixedSize(pression, readingSize)  + 
         convInt2StringFixedSize(hum     , readingSize)  +
         convInt2StringFixedSize(x       , positionSize) + 
         convInt2StringFixedSize(y       , positionSize) + 
         convInt2StringFixedSize(z       , positionSize);
}

// function to conv the number in fixes size string 
String convInt2StringFixedSize (long int num, int fsize)
{
  String result = String(num);
  
  // while string smaller than size, fill with zeros
  while (result.length() < fsize)
    result = "0" + result;

  // if string is too big, error: become zero
  if (result.length() > fsize)
    result = convInt2StringFixedSize (0, fsize);

  return result;
}

void cmdBlink(int time)
{
  digitalWrite(PinLED, HIGH); // turn the LED on (HIGH is the voltage level)
  delay(time);                // wait for a second
  digitalWrite(PinLED, LOW);  // turn the LED off by making the voltage LOW
  delay(time);                // wait for a second
}
