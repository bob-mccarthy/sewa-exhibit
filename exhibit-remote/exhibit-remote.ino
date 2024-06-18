

#include "AiEsp32RotaryEncoder.h"
#include "Arduino.h"
#include <TFT_eSPI.h> // Hardware-specific library
#include <SPI.h>

#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "NETGEAR94";
const char* password = "widecream822";
String serverName = "http://192.168.0.223/send/";

TFT_eSPI tft = TFT_eSPI(); 

#define ROTARY_ENCODER_A_PIN D1 //DT
#define ROTARY_ENCODER_B_PIN D7 //CLK
#define ROTARY_ENCODER_BUTTON_PIN D2 //SW
#define ROTARY_ENCODER_VCC_PIN -1
#define ROTARY_ENCODER_STEPS 10

#define SWITCH_PIN D0
#define LED_PIN D6

int currIndex = 0;
const int NUM_INSTRUCTIONS = 3;
const char* commands[] = {"start", "stop", "refresh"};
uint32_t commandColors[] = {TFT_GREEN, TFT_RED, TFT_LIGHTGREY};

const int refreshCommandTime = 5000;//the rate in millis that we want to erase the command sent text from the screen
long refreshTime = 0;//the specfic time we need to refresh the screen at

//instead of changing here, rather change numbers above
AiEsp32RotaryEncoder rotaryEncoder = AiEsp32RotaryEncoder(ROTARY_ENCODER_A_PIN, ROTARY_ENCODER_B_PIN, ROTARY_ENCODER_BUTTON_PIN, ROTARY_ENCODER_VCC_PIN, ROTARY_ENCODER_STEPS);

int prevValue = 0;
int currValue = 0;

bool updateScreen = false;

void IRAM_ATTR readEncoderISR()
{
    rotaryEncoder.readEncoder_ISR();
}

void setup()
{
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  tft.invertDisplay(1);
  tft.setTextColor(TFT_BLACK);
  //Set text datum to be middle center of text
  tft.setTextDatum(4);

  tft.setTextSize(2);

  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  tft.print("Connecting to ");
  tft.println(ssid);
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    tft.print(".");
    Serial.print(".");
  }
  tft.fillScreen(TFT_BLACK);
  //we must initialize rotary encoder
  rotaryEncoder.begin();
  rotaryEncoder.setup(readEncoderISR);
  //set boundaries and if values should cycle or not
  //in this example we will set possible values between 0 and 1000;
  bool circleValues = false;
  rotaryEncoder.setBoundaries(0, NUM_INSTRUCTIONS-1, circleValues); //minValue, maxValue, circleValues true|false (when max go to min and vice versa)

  /*Rotary acceleration introduced 25.2.2021.
  * in case range to select is huge, for example - select a value between 0 and 1000 and we want 785
  * without accelerateion you need long time to get to that number
  * Using acceleration, faster you turn, faster will the value raise.
  * For fine tuning slow down.
  */
  //rotaryEncoder.disableAcceleration(); //acceleration is now enabled by default - disable if you dont need it
  rotaryEncoder.setAcceleration(0); //or set the value - larger number = more accelearation; 0 or 1 means disabled acceleration
  tft.fillRoundRect(40,40 , 240, 160, 25, commandColors[0]);
  // tft.setTextColor(TFT_WHITE, commandColors[0]);
  tft.drawString(commands[currIndex], 160, 120, 4);
  esp_deep_sleep_enable_gpio_wakeup(BIT(D0), ESP_GPIO_WAKEUP_GPIO_HIGH);
  
  pinMode(SWITCH_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);

  // esp_deep_sleep_start();
}

void loop()
{
  if(digitalRead(SWITCH_PIN) == LOW){
    digitalWrite(LED_PIN, LOW);
    esp_deep_sleep_start();
    
  }
  else{
    digitalWrite(LED_PIN, HIGH);
  }

  // Serial.println(digitalRead(D7));
  if (rotaryEncoder.isEncoderButtonClicked() && millis() >= refreshTime){
      Serial.println("clicked");
      tft.setTextColor(TFT_WHITE);
      tft.setTextSize(2);
      tft.drawString("command sending", 160, 20, 1);
      if(WiFi.status()== WL_CONNECTED){
      HTTPClient http;

      String serverPath = serverName + commands[currIndex];
      Serial.println(serverPath);
      
      // Your Domain name with URL path or IP address with path
      http.begin(serverPath.c_str());
      
      // If you need Node-RED/server authentication, insert user and password below
      //http.setAuthorization("REPLACE_WITH_SERVER_USERNAME", "REPLACE_WITH_SERVER_PASSWORD");
      
      // Send HTTP GET request
      int httpResponseCode = http.GET();
      
      tft.fillRect(0,0, 320, 40, TFT_BLACK);
      if (httpResponseCode>0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);
        tft.drawString("command sent: success", 160, 20, 1);
      }
      else {
        tft.drawString("command sent: error", 160, 20, 1);
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }
      // Free resources
      http.end();
    }
      
      
      refreshTime = millis() + refreshCommandTime;
  }
  if(millis() >= refreshTime){
    tft.fillRect(0,0, 320, 40, TFT_BLACK);
  }

  if (rotaryEncoder.encoderChanged()){
    
    currIndex = rotaryEncoder.readEncoder();
    Serial.println(currIndex);
    Serial.println(commands[currIndex]);
    tft.setTextColor(TFT_BLACK);
    tft.setTextSize(2);
    // Serial.println(rotaryEncoder.readEncoder());
    tft.fillRoundRect(40,40 , 240, 160, 25, commandColors[currIndex]);
    // tft.setTextColor(TFT_WHITE, commandColors[currIndex]);
    tft.drawString(commands[currIndex], 160, 120, 4);
    
  }
  //in loop call your custom function which will process rotary encoder values
  // Serial.println(rotary_loop());
  // delay(50); //or do whatever you need to do...
}


