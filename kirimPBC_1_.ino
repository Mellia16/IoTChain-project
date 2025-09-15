#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_BMP085.h>

// Ganti dengan kredensial WiFi Anda
const char* ssid = "LaptopWicak";
const char* password = "Naufal04";

// Alamat IP dan port server TCP (PC Anda)
const char* host = "10.6.6.41"; // Contoh: "192.168.1.100"
const int port = 61003; // Port yang sama dengan di PC

// --- I2C Pin Definitions (Shared by OLED and BMP180) ---
#define I2C_SDA_PIN 14
#define I2C_SCL_PIN 15

// --- OLED Display Settings ---
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET    -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define OLED_I2C_ADDRESS 0x3C 
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// --- BMP180 Sensor Settings ---
#define BMP180_I2C_ADDRESS 0x77
Adafruit_BMP085 bmp;

// --- LDR Sensor Settings ---
const int ldrPin = 36; // GPIO36 for LDR ADC input (ADC1_CH0)

// Variables to store sensor readings
float temperature = 0.0;
float pressure = 0.0;
int ldrValue = 0;
String ldrDescription = "Unknown"; // Qualitative description of light level
String oledStatus = "OLED Init Failed";
String bmpStatus = "BMP Init Failed";

// Timer for sensor readings and data transmission
unsigned long previousMillis = 0;
const long interval = 2000; // Interval for sending data (2 seconds)

void setup() {
  Serial.begin(115200);

  pinMode(ldrPin, INPUT); 
  analogSetAttenuation(ADC_11db); 
  Serial.println("LDR Pin (GPIO36) initialized with ADC attenuation set to 11dB.");

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN); 
  Serial.println("I2C Bus initialized on SDA: GPIO14, SCL: GPIO15");

  // Initialize OLED
  if(!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS)) { 
    Serial.println(F("SSD1306 allocation failed or not found"));
  } else {
    oledStatus = "OLED OK";
    Serial.println(oledStatus);
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,0);
    display.println("Initializing...");
    display.display();
    delay(1000);
  }

  // Initialize BMP180
  if (!bmp.begin(BMP180_I2C_ADDRESS, &Wire)) { 
    Serial.println(F("Could not find a valid BMP180 sensor, check wiring or address!"));
  } else {
    bmpStatus = "BMP180 OK";
    Serial.println(bmpStatus);
  }

  // Menghubungkan ke WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    updateOLEDStatus("Connecting WiFi...");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Initial sensor read and display
  readSensorData();
  updateOLED();
}

void updateOLEDStatus(String message) {
  if (oledStatus != "OLED OK") return;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println(message);
  display.display();
}

void readSensorData() {
  if (bmpStatus == "BMP180 OK") {
    temperature = bmp.readTemperature();
    if (temperature < -50 || temperature > 150) { 
        Serial.println("BMP180 Temp Read Error");
        temperature = -999; 
        pressure = -999;
    } else {
        pressure = bmp.readPressure() / 100.0F; 
         if (pressure < 300 || pressure > 1100) { 
            Serial.println("BMP180 Pressure Read Error");
            pressure = -999; 
        }
    }
  } else {
    temperature = -998; 
    pressure = -998;    
  }
  
  ldrValue = analogRead(ldrPin); 

  if (ldrValue < 400) { 
    ldrDescription = "Sangat Gelap"; 
  } else if (ldrValue < 1000) { 
    ldrDescription = "Redup";
  } else if (ldrValue < 2500) { 
    ldrDescription = "Cukup Terang";
  } else if (ldrValue < 3500) { 
    ldrDescription = "Terang";
  } else {
    ldrDescription = "Sangat Terang";
  }
}

void updateOLED() {
  if (oledStatus != "OLED OK") return; 

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  display.setCursor(0,0);
  display.print("IP: ");
  if (WiFi.status() == WL_CONNECTED) {
    display.println(WiFi.localIP());
  } else {
    display.println("Disconnected");
  }

  display.setCursor(0, 8); 
  display.print("T: "); 
  if (temperature > -500) display.print(temperature,1); else display.print("Err");
  display.print((char)247); 
  display.print("C");
  
  display.setCursor(0, 16); 
  display.print("P: "); 
  if (pressure > -500) display.print(pressure,0); else display.print("Err"); 
  display.print("hPa");
  
  display.setCursor(0, 24); 
  display.print("LDR: "); display.print(ldrValue);

  display.setCursor(0, 32); 
  display.print("Cahaya: ");display.print(ldrDescription);
  
  display.display();
}

void sendSensorData() {
  WiFiClient client;
  
  if (!client.connect(host, port)) {
    Serial.println("Connection to host failed");
    updateOLEDStatus("Server Disconnected");
    delay(1000);
    return;
  }
  
  Serial.println("Connected to server!");
  
  // Create JSON formatted message with sensor data
  String message = "{";
  message += "\"temperature\":" + String(temperature, 1) + ",";
  message += "\"pressure\":" + String(pressure, 0) + ",";
  message += "\"ldrValue\":" + String(ldrValue) + ",";
  message += "\"lightLevel\":\"" + ldrDescription + "\"";
  message += "}";
  
  client.print(message);
  Serial.println("Message sent: " + message);
  
  // Close connection
  client.stop();
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Read sensors and update OLED every 250ms
  if (currentMillis - previousMillis >= 250) {
    previousMillis = currentMillis;
    readSensorData();
    updateOLED();
  }
  
  // Send data to server every 2 seconds
  static unsigned long lastSendTime = 0;
  if (currentMillis - lastSendTime >= interval) {
    lastSendTime = currentMillis;
    sendSensorData();
  }
}
