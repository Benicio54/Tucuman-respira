#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DNSServer.h>
#include <WebServer.h>
#include <WiFiManager.h>

// --- Credenciales Supabase ---
const char* supabase_url = "https://lskvyvpjjziuclaatrtu.supabase.co/rest/v1/mediciones";
const char* supabase_key = "sb_publishable_O9Havbh6tsAZEDA8VFWQzg_LmTmU4mM"; 

// --- Configuración de puertos serie ---
#define PMS_RX_PIN  18  
#define PMS_TX_PIN  5   
#define PMS_SET_PIN 4   
#define PMS_SERIAL  Serial2 

// Arduino Nano en Serial1 (RX=16, TX=17)
#define NANO_RX_PIN 16
#define NANO_TX_PIN 17
#define NANO_SERIAL Serial1

// Variables globales
uint16_t currentPM25 = 0;
int currentAQI = 0;

// Variables provenientes del Nano
int nano_co2 = 0;
float nano_co = 0.0;
float nano_temp = 0.0;
float nano_hum = 0.0;
float nano_pres = 0.0;
float nano_uv = 0.0;
int nano_lux = 0;

int calculateAQI(float pm25);
void parsePMSFrame(uint8_t* frame);
bool verifyChecksum(uint8_t* frame, uint16_t length);
void enviarASupabase();

void setup() {
  Serial.begin(115200);
  
  pinMode(PMS_SET_PIN, OUTPUT);
  digitalWrite(PMS_SET_PIN, HIGH);
  
  PMS_SERIAL.begin(9600, SERIAL_8N1, PMS_RX_PIN, PMS_TX_PIN);
  NANO_SERIAL.begin(9600, SERIAL_8N1, NANO_RX_PIN, NANO_TX_PIN);
  
  delay(2000);
  Serial.println("\n--- Tucumán Respira: ESP32 Central ---");

  WiFiManager wm;
  wm.setConfigPortalTimeout(180);
  bool res = wm.autoConnect("Tucuman-Respira-Config", "Tucuman2026");

  if (res) {
    Serial.println("\n¡Conectado a Wi-Fi exitosamente!");
  }
}

void loop() {
  // 1. Leer datos del Sensor Plantower (Serial2)
  static uint8_t buffer[128];
  static int index = 0;
  
  while (PMS_SERIAL.available()) {
    buffer[index] = PMS_SERIAL.read();
    if (index >= 31) {
      for (int start = 0; start <= index - 31; start++) {
        if (buffer[start] == 0x42 && buffer[start+1] == 0x4D) {
          uint16_t frame_len = (buffer[start+2] << 8) | buffer[start+3];
          int total_len = frame_len + 4;
          
          if (index - start + 1 >= total_len) {
            parsePMSFrame(&buffer[start]);
            int remaining = index - start - total_len + 1;
            for (int i = 0; i <= remaining; i++) {
              buffer[i] = buffer[start + total_len + i];
            }
            index = remaining;
            break;
          }
        }
      }
    }
    index = (index + 1) % 128;
  }

  // 2. Leer datos del Arduino Nano (Serial1)
  while (NANO_SERIAL.available()) {
    String tramaNano = NANO_SERIAL.readStringUntil('\n');
    tramaNano.trim();

    if (tramaNano.length() > 0) {
      int p1 = tramaNano.indexOf(',');
      int p2 = tramaNano.indexOf(',', p1 + 1);
      int p3 = tramaNano.indexOf(',', p2 + 1);
      int p4 = tramaNano.indexOf(',', p3 + 1);
      int p5 = tramaNano.indexOf(',', p4 + 1);
      int p6 = tramaNano.indexOf(',', p5 + 1);
      int p7 = tramaNano.indexOf(',', p6 + 1);

      if (p7 != -1) {
        nano_co2  = tramaNano.substring(0, p1).toInt();
        nano_co   = tramaNano.substring(p1 + 1, p2).toFloat();
        // Omitimos PM2.5 del índice p3->p4 ya que usamos el Plantower físico
        nano_temp = tramaNano.substring(p3 + 1, p4).toFloat();
        nano_hum  = tramaNano.substring(p4 + 1, p5).toFloat();
        nano_pres = tramaNano.substring(p5 + 1, p6).toFloat();
        nano_uv   = tramaNano.substring(p6 + 1, p7).toFloat();
        nano_lux  = tramaNano.substring(p7 + 1).toInt();
      }
    }
  }

  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
  }

  delay(10);
}

bool verifyChecksum(uint8_t* frame, uint16_t length) {
  uint16_t checksum = 0;
  for (int i = 0; i < length - 2; i++) {
    checksum += frame[i];
  }
  uint16_t received_checksum = (frame[length-2] << 8) | frame[length-1];
  return checksum == received_checksum;
}

int calculateAQI(float pm25) {
  struct Breakpoint { float lowPM25; float highPM25; int lowAQI; int highAQI; };
  static const Breakpoint breakpoints[] = {
    {0.0, 12.0, 0, 50}, {12.1, 35.4, 51, 100}, {35.5, 55.4, 101, 150},
    {55.5, 150.4, 151, 200}, {150.5, 250.4, 201, 300}, {250.5, 350.4, 301, 400}, {350.5, 500.4, 401, 500}
  };
  if (pm25 < 0) pm25 = 0;
  if (pm25 > 500.4) pm25 = 500.4;
  for (int i = 0; i < 7; i++) {
    if (pm25 >= breakpoints[i].lowPM25 && pm25 <= breakpoints[i].highPM25) {
      float aqi = ((float)(breakpoints[i].highAQI - breakpoints[i].lowAQI) / 
                   (breakpoints[i].highPM25 - breakpoints[i].lowPM25)) * 
                   (pm25 - breakpoints[i].lowPM25) + breakpoints[i].lowAQI;
      return (int)(aqi + 0.5);
    }
  }
  return 0;
}

void parsePMSFrame(uint8_t* frame) {
  uint16_t frame_len = (frame[2] << 8) | frame[3];
  int total_len = frame_len + 4;
  
  if (!verifyChecksum(frame, total_len)) return;
  
  // Extraer PM2.5 real del Plantower (descartando su temperatura interna errónea)
  currentPM25 = (frame[12] << 8) | frame[13];
  currentAQI = calculateAQI((float)currentPM25);

  // Enviar a Supabase cada 15 segundos con los datos consolidados
  static unsigned long lastUpload = 0;
  if (millis() - lastUpload >= 15000) {
    lastUpload = millis();
    if (WiFi.status() == WL_CONNECTED) {
      enviarASupabase();
    }
  }
}

void enviarASupabase() {
  HTTPClient http;
  http.begin(supabase_url);

  http.addHeader("Content-Type", "application/json");
  http.addHeader("apikey", supabase_key);
  http.addHeader("Authorization", String("Bearer ") + supabase_key);
  http.addHeader("Prefer", "return=minimal");

  StaticJsonDocument<256> doc;
  doc["co2"] = nano_co2;
  doc["co"] = nano_co;
  doc["pm25"] = currentPM25;       // Del sensor Plantower físico
  doc["temperatura"] = nano_temp;  // Del Arduino Nano (seguro y estable)
  doc["humedad"] = nano_hum;       // Del Arduino Nano (seguro y estable)
  doc["presion"] = nano_pres;
  doc["uv"] = nano_uv;
  doc["luz"] = nano_lux;

  String jsonBody;
  serializeJson(doc, jsonBody);

  int httpResponseCode = http.POST(jsonBody);

  if (httpResponseCode == 201 || httpResponseCode == 200) {
    Serial.println("✅ Datos enviados correctamente a Supabase");
  } else {
    Serial.printf("❌ Error HTTP: %d\n", httpResponseCode);
  }

  http.end();
}