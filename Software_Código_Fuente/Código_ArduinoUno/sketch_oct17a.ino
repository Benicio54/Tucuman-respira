#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>

const int MQ7_AO = A0;
const int MQ7_DO = 9;
const int LDR_AO = A1;
const int LDR_DO = 12;
const int ML8511_OUT = A2;

SoftwareSerial espSerial(2, 3);

const int GPS_RX = 7, GPS_TX = 8;
SoftwareSerial gpsSerial(GPS_RX, GPS_TX);

const int CO2_RX = 10, CO2_TX = 11;
SoftwareSerial co2Serial(CO2_RX, CO2_TX);

Adafruit_BME280 bme;
byte cmdCO2[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};

const unsigned long INTERVALO_TRAMA = 3000;
unsigned long ultimaTrama = 0;

float gpsLat = 0.0;
float gpsLon = 0.0;
bool gpsFix = false;

char nmeaBuffer[96];
byte nmeaIndex = 0;

float ultimaLatValida = 0.0;
float ultimaLonValida = 0.0;
bool tieneUltimaValida = false;

int co2Value = 400;
float ppmCO = 0.0;
float temp = 0.0;
float humedad = 0.0;
float presion = 0.0;
float uvIntensidad = 0.0;
int luxEstimado = 0;

void procesarGPS();
void parsearGGA(const char* linea);
float nmeaAGrados(float valor);
void leerSensores();
void armarYEnviarTrama();
int leerCO2();

void setup() {
  Serial.begin(9600);
  espSerial.begin(9600);
  co2Serial.begin(9600);
  gpsSerial.begin(9600);

  pinMode(MQ7_DO, INPUT);
  pinMode(LDR_DO, INPUT);

  gpsSerial.listen();

  Serial.println("=== INICIANDO SISTEMA MAESTRO (Arduino Uno) ===");

  bool bmeFound = false;
  if (bme.begin(0x76)) {
    Serial.println("BME280 detectado en la direccion 0x76");
    bmeFound = true;
  } else if (bme.begin(0x77)) {
    Serial.println("BME280 detectado en la direccion 0x77");
    bmeFound = true;
  }

  if (!bmeFound) {
    Serial.println("ERROR: BME280 no detectado.");
  }

  Serial.println("Esperando senal GPS...");
  Serial.println("Calentando MQ-7 (esperar 30 seg)...");
  delay(30000);
  Serial.println("Sistema listo!");
}

void loop() {
  procesarGPS();

  if (millis() - ultimaTrama >= INTERVALO_TRAMA) {
    ultimaTrama = millis();

    leerSensores();

    co2Serial.listen();
    co2Value = leerCO2();
    gpsSerial.listen();

    armarYEnviarTrama();
  }

  delay(20);
}

void leerSensores() {
  int ldrAnalog = analogRead(LDR_AO);

  if (ldrAnalog < 30) {
    luxEstimado = map(ldrAnalog, 0, 29, 5000, 1000);
  } else if (ldrAnalog >= 30 && ldrAnalog < 400) {
    luxEstimado = map(ldrAnalog, 30, 399, 1000, 100);
  } else if (ldrAnalog >= 400 && ldrAnalog < 800) {
    luxEstimado = map(ldrAnalog, 400, 799, 100, 10);
  } else {
    luxEstimado = map(ldrAnalog, 800, 1023, 10, 0);
  }

  int mq7Analog = analogRead(MQ7_AO);
  float VRL = mq7Analog * (5.0 / 1023.0);
  if (VRL == 0) VRL = 0.001;
  float Rs = ((5.0 - VRL) / VRL) * 1000.0;
  float R0 = 9800.0;
  float ratio = Rs / R0;
  ppmCO = 98.539 * pow(ratio, -0.63);
  if (ppmCO < 0) ppmCO = 0;

  int uvRaw = analogRead(ML8511_OUT);
  float uvVoltaje = uvRaw * (3.3 / 1023.0);
  uvIntensidad = (uvVoltaje - 0.99) * (15.0 / (3.3 - 0.99));
  if (uvIntensidad < 0) uvIntensidad = 0;

  temp = bme.readTemperature();
  humedad = bme.readHumidity();
  presion = bme.readPressure() / 100.0F;

  if (isnan(temp)) temp = 0;
  if (isnan(humedad)) humedad = 0;
  if (isnan(presion)) presion = 0;
}

void armarYEnviarTrama() {
  float latEnviar = gpsLat;
  float lonEnviar = gpsLon;

  if (gpsFix) {
    if (tieneUltimaValida == false || latEnviar != 0 || lonEnviar != 0) {
      ultimaLatValida = latEnviar;
      ultimaLonValida = lonEnviar;
      tieneUltimaValida = true;
    }
  } else {
    if (tieneUltimaValida) {
      latEnviar = ultimaLatValida;
      lonEnviar = ultimaLonValida;
    } else {
      latEnviar = 0.0;
      lonEnviar = 0.0;
    }
  }

  String trama = String(co2Value) + "," +
                 String(ppmCO, 2) + "," +
                 String(temp, 1) + "," +
                 String(humedad, 0) + "," +
                 String(presion, 0) + "," +
                 String(uvIntensidad, 1) + "," +
                 String(luxEstimado) + "," +
                 String(latEnviar, 5) + "," +
                 String(lonEnviar, 5);

  espSerial.println(trama);

  Serial.print("Trama enviada a ESP32 -> ");
  Serial.print(trama);
  if (gpsFix) {
    Serial.println("  [GPS con fix]");
  } else {
    Serial.println("  [GPS sin fix]");
  }
}

int leerCO2() {
  byte respuesta[9];
  int co2 = 0;
  co2Serial.write(cmdCO2, 9);
  delay(100);
  if (co2Serial.available() > 0) {
    co2Serial.readBytes(respuesta, 9);
    if (respuesta[0] == 0xFF && respuesta[1] == 0x86) {
      co2 = respuesta[2] * 256 + respuesta[3];
    }
  }
  return co2;
}

void procesarGPS() {
  while (gpsSerial.available()) {
    char c = (char)gpsSerial.read();

    if (c == '$') {
      nmeaIndex = 0;
      nmeaBuffer[nmeaIndex++] = c;
      continue;
    }

    if (nmeaIndex == 0) continue;

    if (c == '\n' || c == '\r') {
      nmeaBuffer[nmeaIndex] = '\0';
      parsearGGA(nmeaBuffer);
      nmeaIndex = 0;
      continue;
    }

    if (nmeaIndex < sizeof(nmeaBuffer) - 1) {
      nmeaBuffer[nmeaIndex++] = c;
    }
  }
}

void parsearGGA(const char* linea) {
  if (strncmp(linea, "$GPGGA", 6) != 0 && strncmp(linea, "$GNGGA", 6) != 0) {
    return;
  }

  char campos[15][16];
  int campo = 0;
  int pos = 0;

  for (int i = 0; linea[i] != '\0' && linea[i] != '*' && campo < 15; i++) {
    char c = linea[i];
    if (c == ',') {
      campos[campo][pos] = '\0';
      campo++;
      pos = 0;
    } else if (pos < 15) {
      campos[campo][pos++] = c;
    }
  }
  campos[campo][pos] = '\0';

  if (campo < 6) return;

  if (campos[6][0] != '1' && campos[6][0] != '2') {
    gpsFix = false;
    gpsLat = 0;
    gpsLon = 0;
    return;
  }

  float latRaw = atof(campos[2]);
  float lonRaw = atof(campos[4]);

  if (latRaw == 0 || lonRaw == 0) {
    gpsFix = false;
    gpsLat = 0;
    gpsLon = 0;
    return;
  }

  gpsLat = nmeaAGrados(latRaw);
  if (campos[3][0] == 'S') gpsLat = -gpsLat;

  gpsLon = nmeaAGrados(lonRaw);
  if (campos[5][0] == 'W') gpsLon = -gpsLon;

  gpsFix = true;
}

float nmeaAGrados(float valor) {
  int grados = (int)(valor / 100.0);
  float minutos = valor - (grados * 100.0);
  return grados + (minutos / 60.0);
}
