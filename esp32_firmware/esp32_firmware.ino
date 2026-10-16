#include <WiFi.h>
#include <HTTPClient.h>

// Wi-Fi Credentials
const char* WIFI_SSID = "OPPOA9";
const char* WIFI_PASS = "k8kjcnnc";

// Supabase Credentials
const char* SUPABASE_URL = '<URL>';
const char* SUPABASE_KEY = '<KEY>';

// GPIO pin
const int SENSOR_PIN = 1; 

void setup() {
  Serial.begin(115200);
  delay(2000); 

  // Connect to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");
}

void loop() {
  // 1. Dynamic Pull-Up Trick to grab the analog value safely
  pinMode(SENSOR_PIN, INPUT_PULLUP);
  delay(30); 
  
  int rawValue = analogRead(SENSOR_PIN);
  
  pinMode(SENSOR_PIN, INPUT); // Shut off pin immediately to prevent probe rust

  // 2. Map values 
  int moisturePercent = map(rawValue, 6000, 1000, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);

  // Print local debug readings to Serial Monitor
  Serial.print("Raw Reading: ");
  Serial.print(rawValue);
  Serial.print(" | Moisture: ");
  Serial.print(moisturePercent);
  Serial.println("%");

  // 3. Database HTTP Post transmission logic
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SUPABASE_URL);
    
    // Set Supabase Headers
    http.addHeader("Content-Type", "application/json");
    http.addHeader("apikey", SUPABASE_KEY);
    http.addHeader("Authorization", String("Bearer ") + SUPABASE_KEY);
    http.addHeader("Prefer", "return=minimal");

    // Construct JSON payload
    String jsonPayload = "{\"raw_value\":" + String(rawValue) + 
                         ", \"moisture_percent\":" + String(moisturePercent) + "}";

    // Send HTTP POST request
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("Data sent to Supabase successfully. Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error sending POST request: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("Wi-Fi disconnected! Skipping database upload.");
  }

  delay(600000);
}
