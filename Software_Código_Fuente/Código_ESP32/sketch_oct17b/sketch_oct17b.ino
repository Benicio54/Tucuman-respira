#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DNSServer.h>
#include <WebServer.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>

// =====================================================
// CONFIGURACION DE SUPABASE
// =====================================================

const char* SUPABASE_URL =
    "https://lskvyvpjjziuclaatrtu.supabase.co/rest/v1/mediciones";

const char* SUPABASE_KEY =
    "sb_publishable_O9Havbh6tsAZEDA8VFWQzg_LmTmU4mM";

// =====================================================
// PUNTO DE ACCESO PERMANENTE
// =====================================================

const char* AP_SSID = "Tucuman-Respira-Config";
const char* AP_PASSWORD = "Tucuman2026";

const char* CLAVE_DISPOSITIVO = "tucu2026";

IPAddress apIP(192, 168, 4, 1);
IPAddress apGateway(192, 168, 4, 1);
IPAddress apSubnet(255, 255, 255, 0);

DNSServer dnsServer;
WebServer server(80);

// =====================================================
// ZUMBADOR Y ALARMA
// =====================================================

const int BUZZER_PIN = 23;
const unsigned long SILENCIO_MS = 600000;
const int UMBRAL_ALERTA_ON = 100;
const int UMBRAL_ALERTA_OFF = 80;

bool zumbando = false;
bool alertaActiva = false;
bool silenciado = false;
unsigned long silencioInicio = 0;

// =====================================================
// COMUNICACION SERIAL
// =====================================================

HardwareSerial pmsSerial(2);
HardwareSerial unoSerial(1);

const int PMS_SET_PIN = 4;

// =====================================================
// VARIABLES DE LOS SENSORES
// =====================================================

int currentCO2 = 0;
float currentCO = 0.0;
uint16_t currentPM25 = 0;
float currentTemp = 0.0;
float currentHumidity = 0.0;
float currentPressure = 0.0;
float currentUV = 0.0;
int currentLight = 0;
float currentLat = 0.0;
float currentLon = 0.0;
int currentAQI = 0;

unsigned long lastUpload = 0;
const unsigned long uploadInterval = 15000;

unsigned long lastReport = 0;
const unsigned long reportInterval = 15000;

bool sensorDataUpdated = false;

String wifiSSID;
String wifiPassword;

int tramasInvalidas = 0;

// =====================================================
// ESTADO DE LA RED
// =====================================================

enum EstadoRed {
  RED_AP,
  RED_CONECTANDO,
  RED_CONECTADA
};

EstadoRed estadoRed = RED_AP;
bool apActivo = false;

unsigned long intentoInicio = 0;
unsigned long desconectadoDesde = 0;

const unsigned long TIEMPO_INTENTO_MS = 20000;
const unsigned long TIEMPO_CONFIRMAR_CAIDA_MS = 5000;

// =====================================================
// INDICE DE CALIDAD DEL AIRE (EPA 2024)
// Mismo criterio que la aplicacion web.
// =====================================================

const float BR_PM25[][4] = {
  {0.0,   9.0,   0,  50},
  {9.1,   35.4,  51, 100},
  {35.5,  55.4,  101, 150},
  {55.5,  125.4, 151, 200},
  {125.5, 225.4, 201, 300},
  {225.5, 500.4, 301, 500}
};

const float BR_CO[][4] = {
  {0.0,   4.4,   0,   50},
  {4.5,   34.9,  51,  100},
  {35.0,  50.0,  101, 150},
  {50.1,  100.0, 151, 200},
  {100.1, 200.0, 201, 300},
  {200.1, 500.0, 301, 500}
};

float subIndice(const float br[][4], int cantidad, float c) {
  for (int i = 0; i < cantidad; i++) {
    if (c >= br[i][0] && c <= br[i][1]) {
      return round(
        ((br[i][3] - br[i][2]) / (br[i][1] - br[i][0])) *
        (c - br[i][0]) + br[i][2]
      );
    }
  }
  return c > br[cantidad - 1][1] ? 500 : 0;
}

int calcularAQI() {
  float aqiPm = subIndice(BR_PM25, 6, (float)currentPM25);
  float aqiCo = subIndice(BR_CO, 6, currentCO);
  return (int)round(aqiPm > aqiCo ? aqiPm : aqiCo);
}

// =====================================================
// ZUMBADOR
// =====================================================

void actualizarAlarma() {
  if (alertaActiva && currentAQI < UMBRAL_ALERTA_OFF) {
    alertaActiva = false;
  } else if (!alertaActiva && currentAQI > UMBRAL_ALERTA_ON) {
    alertaActiva = true;
  }

  if (silenciado && millis() - silencioInicio >= SILENCIO_MS) {
    silenciado = false;
  }

  bool debeSonar = alertaActiva && !silenciado;

  if (debeSonar && !zumbando) {
    tone(BUZZER_PIN, 2000);
    zumbando = true;
  } else if (!debeSonar && zumbando) {
    noTone(BUZZER_PIN);
    zumbando = false;
  }
}

// =====================================================
// LECTURA DEL SENSOR PLANTOWER
// =====================================================

bool readPMSFrame() {
  static uint8_t buffer[32];
  static uint8_t index = 0;

  while (pmsSerial.available()) {
    uint8_t incoming = pmsSerial.read();

    if (index == 0 && incoming != 0x42) {
      continue;
    }

    if (index == 1 && incoming != 0x4D) {
      index = 0;

      if (incoming == 0x42) {
        buffer[index++] = incoming;
      }

      continue;
    }

    buffer[index++] = incoming;

    if (index >= sizeof(buffer)) {
      index = 0;

      uint16_t frameLength =
          ((uint16_t)buffer[2] << 8) | buffer[3];

      if (frameLength != 28) {
        continue;
      }

      uint16_t checksum = 0;

      for (int i = 0; i < 30; i++) {
        checksum += buffer[i];
      }

      uint16_t receivedChecksum =
          ((uint16_t)buffer[30] << 8) | buffer[31];

      if (checksum != receivedChecksum) {
        continue;
      }

      currentPM25 =
          ((uint16_t)buffer[12] << 8) | buffer[13];

      return true;
    }
  }

  return false;
}

// =====================================================
// LECTURA DE DATOS DEL ARDUINO UNO
// Formato esperado (9 campos):
// CO2,CO,temp,humedad,presion,UV,luz,lat,lon
// =====================================================

void readUnoData() {
  static String inputLine;

  while (unoSerial.available()) {
    char c = (char)unoSerial.read();

    if (c == '\n' || c == '\r') {
      inputLine.trim();

      if (inputLine.length() > 0) {
        int co2;
        float co, tmp, hum, pres, uv, lat, lon;
        int luz;

        int parsed = sscanf(
            inputLine.c_str(),
            "%d,%f,%f,%f,%f,%f,%d,%f,%f",
            &co2,
            &co,
            &tmp,
            &hum,
            &pres,
            &uv,
            &luz,
            &lat,
            &lon
        );

        if (parsed == 9) {
          currentCO2 = co2;
          currentCO = co;
          currentTemp = tmp;
          currentHumidity = hum;
          currentPressure = pres;
          currentUV = uv;
          currentLight = luz;
          currentLat = lat;
          currentLon = lon;
          currentAQI = calcularAQI();
          sensorDataUpdated = true;
        } else {
          tramasInvalidas++;

          if (tramasInvalidas <= 5) {
            Serial.printf(
              "Trama del Uno descartada (%d/9 campos): %s\n",
              parsed,
              inputLine.c_str()
            );
          }
        }
      }

      inputLine = "";
    } else if (inputLine.length() < 180) {
      inputLine += c;
    } else {
      inputLine = "";
    }
  }
}

// =====================================================
// ENVIO DE DATOS A SUPABASE
// =====================================================

void enviarASupabase() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("No hay conexion Wi-Fi. Datos no enviados.");
    return;
  }

  HTTPClient http;
  http.begin(SUPABASE_URL);
  http.setTimeout(15000);

  http.addHeader("Content-Type", "application/json");
  http.addHeader("apikey", SUPABASE_KEY);
  http.addHeader(
      "Authorization",
      String("Bearer ") + SUPABASE_KEY
  );
  http.addHeader("Prefer", "return=minimal");

  StaticJsonDocument<1024> doc;

  doc["co2"] = currentCO2;
  doc["co"] = currentCO;
  doc["pm25"] = currentPM25;
  doc["temperatura"] = currentTemp;
  doc["humedad"] = currentHumidity;
  doc["presion"] = currentPressure;
  doc["uv"] = currentUV;
  doc["luz"] = currentLight;
  doc["latitud"] = currentLat;
  doc["longitud"] = currentLon;
  doc["ip_dispositivo"] = WiFi.localIP().toString();

  String jsonData;
  serializeJson(doc, jsonData);

  int httpResponseCode = http.POST(jsonData);

  if (httpResponseCode >= 200 && httpResponseCode < 300) {
    Serial.println("Datos enviados correctamente a Supabase.");
  } else if (httpResponseCode < 0) {
    Serial.printf(
        "Fallo de conexion con Supabase: %s\n",
        http.errorToString(httpResponseCode).c_str()
    );
  } else {
    Serial.printf(
        "Error al enviar datos a Supabase. Codigo HTTP: %d\n",
        httpResponseCode
    );
    Serial.println(http.getString());
  }

  http.end();
}

// =====================================================
// REPORTE DE SENSORES POR PUERTO SERIAL
// =====================================================

void printSensorReport() {
  Serial.println();
  Serial.println("----------------------------------------");
  Serial.println("REPORTE DE SENSORES EN TIEMPO REAL:");

  Serial.printf("CO2 (MH-Z19C): %d ppm\n", currentCO2);
  Serial.printf("Monoxido de carbono (MQ-7): %.2f ppm\n", currentCO);
  Serial.printf("Particulas (PM2.5 - Plantower): %u ug/m3\n", currentPM25);
  Serial.printf("Temperatura (BME280): %.1f C\n", currentTemp);
  Serial.printf("Humedad (BME280): %.0f %%\n", currentHumidity);
  Serial.printf("Presion (BME280): %.0f hPa\n", currentPressure);
  Serial.printf("Radiacion UV (ML8511): %.1f\n", currentUV);
  Serial.printf("Luz ambiental (LDR): %d lux\n", currentLight);
  Serial.printf("Latitud (GPS): %.5f\n", currentLat);
  Serial.printf("Longitud (GPS): %.5f\n", currentLon);
  Serial.printf("ICA calculado: %d\n", currentAQI);
  Serial.printf("Alarma: %s | Silenciado: %s\n",
                alertaActiva ? "ACTIVA" : "normal",
                silenciado ? "si" : "no");

  if (tramasInvalidas > 0) {
    Serial.printf("Tramas invalidas del Uno: %d\n", tramasInvalidas);
  }

  Serial.println("----------------------------------------");
}

// =====================================================
// PAGINA DE CONFIGURACION WI-FI
// =====================================================

String getConfigPage() {
  String page = R"rawliteral(
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tucumán Respira</title>
<style>
body {
  font-family: Arial, sans-serif;
  background: #eef5f0;
  color: #18352a;
  margin: 0;
  padding: 20px;
}
.container {
  max-width: 420px;
  margin: 30px auto;
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 16px #0002;
}
h1 { color: #16805d; }
label {
  display: block;
  margin-top: 16px;
  font-weight: bold;
}
input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  margin-top: 6px;
  border: 1px solid #bbb;
  border-radius: 8px;
}
button {
  width: 100%;
  margin-top: 20px;
  padding: 13px;
  background: #16805d;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}
.info {
  margin-top: 16px;
  font-size: 14px;
  line-height: 1.5;
}
</style>
</head>
<body>
<div class="container">
<h1>🌱 Tucumán Respira</h1>
<p>Configuración de conexión Wi-Fi del dispositivo.</p>
<form action="/save" method="POST">
<label for="ssid">Nombre de la red Wi-Fi</label>
<input id="ssid" name="ssid" maxlength="32" required
       placeholder="Nombre de tu red">

<label for="password">Contraseña de la red Wi-Fi</label>
<input id="password" name="password" type="password"
       maxlength="64" placeholder="Contraseña Wi-Fi">

<button type="submit">Guardar y conectar</button>
</form>
<div class="info">
<p>Estado WiFi: <strong><!--ESTADO_WIFI--></strong></p>
<p>Al conectar, esta red de configuración se cerrará automáticamente.</p>
<p>Si no se abre automáticamente, ingresá a
<strong>http://192.168.4.1</strong>.</p>
</div>
</div>
</body>
</html>
)rawliteral";

  bool conectado = (WiFi.status() == WL_CONNECTED);
  String estadoWifi = conectado
      ? (String("Conectado a ") + WiFi.SSID())
      : String("No conectado a ninguna red");

  page.replace("<!--ESTADO_WIFI-->", estadoWifi);

  return page;
}

// =====================================================
// GUARDAR CONFIGURACION WI-FI
// =====================================================

void handleSaveWiFi() {
  if (!server.hasArg("ssid") || !server.hasArg("password")) {
    server.send(
        400,
        "text/plain; charset=utf-8",
        "Faltan el nombre o la contraseña de la red."
    );
    return;
  }

  String newSSID = server.arg("ssid");
  String newPassword = server.arg("password");

  newSSID.trim();

  if (newSSID.length() == 0) {
    server.send(
        400,
        "text/plain; charset=utf-8",
        "El nombre de la red no puede estar vacío."
    );
    return;
  }

  wifiSSID = newSSID;
  wifiPassword = newPassword;

  WiFi.setAutoReconnect(false);
  WiFi.mode(WIFI_AP_STA);
  WiFi.begin(wifiSSID.c_str(), wifiPassword.c_str());

  estadoRed = RED_CONECTANDO;
  intentoInicio = millis();
  desconectadoDesde = 0;

  Serial.printf(
      "Intentando conectar a la red: %s\n",
      wifiSSID.c_str()
  );

  String pagina = "<!DOCTYPE html><html lang='es'><meta charset='UTF-8'>"
      "<meta name='viewport' content='width=device-width,initial-scale=1'>"
      "<body style='font-family:Arial;padding:24px;max-width:480px;margin:auto'>"
      "<h2>Conectando…</h2>"
      "<p>Intentando conectar a <strong>";
  pagina += wifiSSID;
  pagina += "</strong>.</p>"
      "<p>Si la red <strong>";
  pagina += AP_SSID;
  pagina += "</strong> desaparece en los próximos segundos, "
      "la conexión fue exitosa.</p>"
      "<p>Si vuelve a aparecer, revisá la contraseña e intentá de nuevo.</p>"
      "<a href='/'>Volver</a></body></html>";

  server.send(200, "text/html; charset=utf-8", pagina);
}

// =====================================================
// ENDPOINTS DE ALARMA
// =====================================================

void enviarCabecerasCORS() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "*");
}

void handleSilenciar() {
  enviarCabecerasCORS();

  if (server.method() == HTTP_OPTIONS) {
    server.send(204);
    return;
  }

  if (server.arg("k") != CLAVE_DISPOSITIVO) {
    server.send(
        403,
        "application/json",
        "{\"ok\":false,\"error\":\"clave incorrecta\"}"
    );
    return;
  }

  silenciado = true;
  silencioInicio = millis();

  if (zumbando) {
    noTone(BUZZER_PIN);
    zumbando = false;
  }

  StaticJsonDocument<256> doc;
  doc["ok"] = true;
  doc["silenciado_minutos"] = SILENCIO_MS / 60000;
  doc["ica"] = currentAQI;
  doc["alerta"] = alertaActiva;

  String out;
  serializeJson(doc, out);
  server.send(200, "application/json", out);

  Serial.println("Alarma silenciada desde la aplicacion.");
}

void handleAlarma() {
  enviarCabecerasCORS();

  if (server.method() == HTTP_OPTIONS) {
    server.send(204);
    return;
  }

  StaticJsonDocument<512> doc;
  doc["ica"] = currentAQI;
  doc["alerta"] = alertaActiva;
  doc["silenciado"] = silenciado;
  doc["zumbando"] = zumbando;
  doc["ip"] = WiFi.localIP().toString();
  doc["punto_acceso"] = AP_SSID;
  doc["ip_punto_acceso"] = WiFi.softAPIP().toString();

  String out;
  serializeJson(doc, out);
  server.send(200, "application/json", out);
}

// =====================================================
// ESTADO DEL DISPOSITIVO
// =====================================================

void handleStatus() {
  StaticJsonDocument<512> doc;

  doc["wifi_conectado"] = WiFi.status() == WL_CONNECTED;
  doc["ssid"] = WiFi.SSID();
  doc["ip"] = WiFi.localIP().toString();
  doc["punto_acceso"] = AP_SSID;
  doc["ip_punto_acceso"] = WiFi.softAPIP().toString();
  doc["ica"] = currentAQI;
  doc["alerta"] = alertaActiva;
  doc["silenciado"] = silenciado;
  doc["tramas_invalidas"] = tramasInvalidas;

  String response;
  serializeJson(doc, response);

  server.send(200, "application/json", response);
}

// =====================================================
// CONFIGURACION DEL PORTAL
// =====================================================

void setupWebServer() {
  server.on("/", HTTP_GET, []() {
    server.send(
        200,
        "text/html; charset=utf-8",
        getConfigPage()
    );
  });

  server.on("/save", HTTP_POST, handleSaveWiFi);

  server.on("/status", HTTP_GET, handleStatus);

  server.on("/alarma", HTTP_GET, handleAlarma);
  server.on("/alarma", HTTP_POST, handleAlarma);
  server.on("/alarma", HTTP_OPTIONS, handleAlarma);

  server.on("/silenciar", HTTP_GET, handleSilenciar);
  server.on("/silenciar", HTTP_POST, handleSilenciar);
  server.on("/silenciar", HTTP_OPTIONS, handleSilenciar);

  server.on("/generate_204", HTTP_GET, []() {
    server.sendHeader("Location", "http://192.168.4.1/", true);
    server.send(302, "text/plain", "");
  });

  server.on("/hotspot-detect.html", HTTP_GET, []() {
    server.sendHeader("Location", "http://192.168.4.1/", true);
    server.send(302, "text/plain", "");
  });

  server.on("/connecttest.txt", HTTP_GET, []() {
    server.sendHeader("Location", "http://192.168.4.1/", true);
    server.send(302, "text/plain", "");
  });

  server.on("/fwlink", HTTP_GET, []() {
    server.sendHeader("Location", "http://192.168.4.1/", true);
    server.send(302, "text/plain", "");
  });

  server.onNotFound([]() {
    server.sendHeader("Location", "http://192.168.4.1/", true);
    server.send(302, "text/plain", "");
  });

  server.begin();
}

// =====================================================
// RED DE CONFIGURACION (PUNTO DE ACCESO)
// =====================================================

bool iniciarAP() {
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apGateway, apSubnet);

  bool apStarted = false;

  for (int intento = 1; intento <= 3 && !apStarted; intento++) {
    apStarted = WiFi.softAP(
        AP_SSID,
        AP_PASSWORD,
        6,
        false,
        4
    );

    if (!apStarted) {
      Serial.printf(
          "Intento %d de iniciar la red de configuración fallido.\n",
          intento
      );
      delay(500);
    }
  }

  if (apStarted) {
    dnsServer.start(53, "*", apIP);
    apActivo = true;

    Serial.println("Red de configuración iniciada.");
    Serial.printf("Red: %s\n", AP_SSID);
    Serial.printf("Contraseña: %s\n", AP_PASSWORD);
    Serial.printf(
        "IP del portal: %s\n",
        WiFi.softAPIP().toString().c_str()
    );
  } else {
    apActivo = false;
    Serial.println("Error al iniciar la red de configuración.");
  }

  return apStarted;
}

void detenerAP() {
  if (!apActivo) {
    return;
  }

  dnsServer.stop();
  WiFi.softAPdisconnect(true);
  apActivo = false;

  Serial.println("Red de configuración cerrada.");
}

// =====================================================
// GESTION DE LA CONEXION WI-FI
// =====================================================

void gestionarRed() {
  unsigned long ahora = millis();

  switch (estadoRed) {
    case RED_CONECTANDO:
      if (WiFi.status() == WL_CONNECTED) {
        Serial.println("Conexión Wi-Fi establecida.");
        Serial.print("IP de la red: ");
        Serial.println(WiFi.localIP());
        Serial.println(
            "Usá esa IP en la aplicación web para controlar la alarma."
        );

        detenerAP();

        estadoRed = RED_CONECTADA;
        desconectadoDesde = 0;
      } else if (ahora - intentoInicio >= TIEMPO_INTENTO_MS) {
        WiFi.disconnect();

        iniciarAP();

        estadoRed = RED_AP;
        Serial.println("No se pudo conectar a la red indicada.");
        Serial.println("Red de configuración disponible.");
      }
      break;

    case RED_CONECTADA:
      if (WiFi.status() == WL_CONNECTED) {
        desconectadoDesde = 0;
      } else if (desconectadoDesde == 0) {
        desconectadoDesde = ahora;
      } else if (
          ahora - desconectadoDesde >= TIEMPO_CONFIRMAR_CAIDA_MS
      ) {
        WiFi.disconnect();

        wifiSSID = "";
        wifiPassword = "";

        iniciarAP();

        estadoRed = RED_AP;
        Serial.println("Se perdió la conexión Wi-Fi.");
        Serial.println("Red de configuración disponible.");
      }
      break;

    case RED_AP:
    default:
      break;
  }
}

// =====================================================
// SETUP
// =====================================================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("========================================");
  Serial.println("       TUCUMAN RESPIRA");
  Serial.println("========================================");

  pinMode(PMS_SET_PIN, OUTPUT);
  digitalWrite(PMS_SET_PIN, HIGH);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  pmsSerial.begin(9600, SERIAL_8N1, 18, 5);
  unoSerial.begin(9600, SERIAL_8N1, 16, 17);

  WiFi.persistent(false);
  WiFi.setAutoReconnect(false);

  iniciarAP();
  setupWebServer();
  WiFi.setSleep(false);

  Serial.println();
  Serial.println("Sistema iniciado.");
  Serial.println("Conectate a la red de configuración para elegir una red Wi-Fi.");
  Serial.println("Configuración: http://192.168.4.1");
  Serial.println("========================================");
}

// =====================================================
// LOOP
// =====================================================

void loop() {
  if (apActivo) {
    dnsServer.processNextRequest();
  }

  server.handleClient();

  readUnoData();

  if (readPMSFrame()) {
    sensorDataUpdated = true;
    currentAQI = calcularAQI();
  }

  actualizarAlarma();

  unsigned long now = millis();

  if (sensorDataUpdated && now - lastReport >= reportInterval) {
    lastReport = now;

    printSensorReport();

    sensorDataUpdated = false;
  }

  if (now - lastUpload >= uploadInterval) {
    lastUpload = now;

    if (WiFi.status() == WL_CONNECTED) {
      enviarASupabase();
    }
  }

  gestionarRed();

  delay(10);
}
