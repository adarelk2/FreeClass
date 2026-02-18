// =====================================================
// ESP32 + AM312 PIR + HTTPS occupied ping (TLS fixed)
// + DEV/PROD mode + DEV-only long press BOOT reset
//
// FIXES (important):
// 1) LedMode defined BEFORE setLedMode (compilation fix)
// 2) BOOT long-press reset works EVEN while WiFi connect is stuck (non-blocking reset check)
// 3) WiFi connect has TIMEOUT -> falls back to Setup Portal automatically
// 4) BOOT reset also works while in Setup Portal mode (AP)
// 5) Wait for BOOT release before reboot (avoid download mode)
//
// DEVICE_MODE:
//   0 = DEV: long press BOOT (GPIO0) for 5s -> deletes /config.json -> reboot
//   1 = PROD: BOOT long-press reset disabled
// =====================================================

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <time.h>

#include <LittleFS.h>
#include <ArduinoJson.h>
#include <WebServer.h>
#include <DNSServer.h>

// ==================== RESET BUTTON ====================
#define RESET_BTN_PIN 0
static const unsigned long RESET_HOLD_MS = 5000; // 5 seconds

// ==================== MODE =====================
// 0 = DEV (testing)
// 1 = PROD (production)
#define DEVICE_MODE 0

// ==================== CONFIG (LittleFS) =================
static const char* CONFIG_PATH = "/config.json";

String WIFI_SSID = "";
String WIFI_PASS = "";
String API_URL   = "";
String TOKEN     = "";

// ==================== SETUP PORTAL (AP + DNS) ==========
static const char* SETUP_AP_SSID = "FreeClass-Setup";
static const char* SETUP_AP_PASS = ""; // open AP
static DNSServer dnsServer;
static const byte DNS_PORT = 53;
static WebServer server(80);

// ==================== WIFI CONNECT POLICY ==============
static const unsigned long WIFI_CONNECT_TIMEOUT_MS = 25000; // 25 seconds

// ==================== PIR CONFIG =======================
#define PIR_PIN 27
static const int HIGH_STABLE_MS = 30;
static const unsigned long UNOCCUPIED_AFTER_MS = 15UL * 60UL * 1000UL; // 15 minutes

// ==================== LED CONFIG =======================
#define LED_PIN 2
#define LED_ACTIVE_LOW false

static const unsigned long WIFI_BLINK_MS = 250;
static const unsigned long MOTION_BLINK_WINDOW_MS = 2500;
static const unsigned long MOTION_BLINK_MS = 150;

// ==================== HTTP/TLS =========================
static const unsigned long HTTP_TIMEOUT_MS = 7000;

// Let's Encrypt ISRG Root X1 (PEM)
static const char* LE_ISRG_ROOT_X1 PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----
)EOF";

// =====================================================
// LED STATE (IMPORTANT: enum BEFORE functions)
// =====================================================
enum class LedMode { OFF, WIFI_BLINK, MOTION_BLINK_WINDOW, SOLID_ON };

static LedMode ledMode = LedMode::OFF;
static unsigned long ledLastToggleMs = 0;
static bool ledBlinkState = false;
static unsigned long motionBlinkUntilMs = 0;

static inline void ledOffHard() { digitalWrite(LED_PIN, LED_ACTIVE_LOW ? HIGH : LOW); }
static inline void ledOnHard()  { digitalWrite(LED_PIN, LED_ACTIVE_LOW ? LOW  : HIGH); }

static void setLedMode(LedMode mode) {
  ledMode = mode;
  ledLastToggleMs = millis();
  ledBlinkState = false;

  if (mode == LedMode::OFF) ledOffHard();
  else if (mode == LedMode::SOLID_ON) ledOnHard();
  else ledOffHard();
}

static void updateLed() {
  const unsigned long now = millis();

  if (ledMode == LedMode::WIFI_BLINK) {
    if (now - ledLastToggleMs >= WIFI_BLINK_MS) {
      ledLastToggleMs = now;
      ledBlinkState = !ledBlinkState;
      if (ledBlinkState) ledOnHard(); else ledOffHard();
    }
    return;
  }

  if (ledMode == LedMode::MOTION_BLINK_WINDOW) {
    if (now >= motionBlinkUntilMs) { setLedMode(LedMode::OFF); return; }
    if (now - ledLastToggleMs >= MOTION_BLINK_MS) {
      ledLastToggleMs = now;
      ledBlinkState = !ledBlinkState;
      if (ledBlinkState) ledOnHard(); else ledOffHard();
    }
    return;
  }
}

// =====================================================
// MOTION / STATE
// =====================================================
static bool occupied = false;
static unsigned long lastMotionMs = 0;
static bool requestInFlight = false;

// Interrupt flag
volatile bool pirEdgeSeen = false;
volatile unsigned long pirEdgeMs = 0;

void IRAM_ATTR onPirRise() {
  pirEdgeSeen = true;
  pirEdgeMs = millis();
}

// =====================================================
// HELPERS
// =====================================================
static String htmlEscape(const String& s) {
  String out = s;
  out.replace("&", "&amp;");
  out.replace("<", "&lt;");
  out.replace(">", "&gt;");
  out.replace("\"", "&quot;");
  out.replace("'", "&#39;");
  return out;
}

static bool readStableHigh(int msNeeded) {
  const unsigned long start = millis();
  while (millis() - start < (unsigned long)msNeeded) {
    if (digitalRead(PIR_PIN) == LOW) return false;
    delay(1);
  }
  return true;
}

// ==================== TIME (NTP) ======================
static bool ensureTimeSynced() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");

  const unsigned long start = millis();
  time_t now = 0;

  while (millis() - start < 15000) {
    time(&now);
    if (now > 1700000000) {
      struct tm t;
      gmtime_r(&now, &t);
      Serial.printf("Time synced (UTC): %04d-%02d-%02d %02d:%02d:%02d\n",
                    t.tm_year + 1900, t.tm_mon + 1, t.tm_mday,
                    t.tm_hour, t.tm_min, t.tm_sec);
      return true;
    }
    delay(200);
  }

  Serial.println("WARN: Time not synced (TLS may fail).");
  return false;
}

// =====================================================
// FACTORY RESET + DEV LONG PRESS CHECK
// =====================================================
static void factoryReset() {
  Serial.println("FACTORY RESET (DEV MODE)");
  if (LittleFS.exists(CONFIG_PATH)) {
    bool ok = LittleFS.remove(CONFIG_PATH);
    Serial.print("Removed config.json: ");
    Serial.println(ok ? "OK" : "FAIL");
  } else {
    Serial.println("config.json not found (nothing to remove)");
  }

  // GPIO0 LOW during reboot can put ESP32 in download mode → wait release
  Serial.println("Release BOOT to reboot...");
  unsigned long t0 = millis();
  while (digitalRead(RESET_BTN_PIN) == LOW) {
    if (millis() - t0 > 15000) break;
    delay(10);
  }

  delay(300);
  ESP.restart();
}

static void checkDevLongPressReset() {
#if DEVICE_MODE == 0
  static unsigned long resetPressStart = 0;

  if (digitalRead(RESET_BTN_PIN) == LOW) {
    if (resetPressStart == 0) resetPressStart = millis();
    if (millis() - resetPressStart >= RESET_HOLD_MS) {
      factoryReset(); // does not return
    }
  } else {
    resetPressStart = 0;
  }
#endif
}

// ==================== WIFI ============================
static void startSetupPortal(); // forward

static void ensureWiFiConnected() {
  if (WiFi.status() == WL_CONNECTED) return;

  setLedMode(LedMode::WIFI_BLINK);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID.c_str(), WIFI_PASS.c_str());

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    checkDevLongPressReset(); // ✅ reset works even if WiFi is stuck
    updateLed();
    delay(10);

    if (millis() - start > WIFI_CONNECT_TIMEOUT_MS) {
      Serial.println("WiFi connect timeout -> starting setup portal");
      setLedMode(LedMode::OFF);
      ledOffHard();
      startSetupPortal(); // go AP mode
      return;
    }
  }

  setLedMode(LedMode::OFF);
  ledOffHard();

  Serial.print("WiFi connected, IP: ");
  Serial.println(WiFi.localIP());

  ensureTimeSynced();
}

// ==================== HTTP (HTTPS) ====================
static bool sendOccupiedEvent() {
  if (WiFi.status() != WL_CONNECTED) return false;

  WiFiClientSecure client;
  client.setTimeout(HTTP_TIMEOUT_MS / 1000);
  client.setHandshakeTimeout(15);
  client.setCACert(LE_ISRG_ROOT_X1);

  HTTPClient http;
  http.setTimeout((int)HTTP_TIMEOUT_MS);

  if (!http.begin(client, API_URL.c_str())) {
    Serial.println("http.begin() failed");
    return false;
  }

  http.addHeader("Content-Type", "application/json");

  String body = String("{\"method\":\"createNewActivty\",\"params\":{\"private_key\":\"") + TOKEN + "\"}}";

  const int code = http.POST(body);
  String resp = (code > 0) ? http.getString() : String("");
  http.end();

  Serial.print("HTTP code: ");
  Serial.println(code);

  if (code < 0) {
    Serial.printf("HTTPClient error: %s\n", http.errorToString(code).c_str());
  }

  if (resp.length()) {
    Serial.print("Response: ");
    Serial.println(resp);
  }

  return (code >= 200 && code < 300);
}

// ==================== CONFIG FS =======================
static void writeDefaultConfigIfMissing() {
  if (LittleFS.exists(CONFIG_PATH)) return;

  StaticJsonDocument<256> doc;
  doc["wifi_ssid"] = "";
  doc["wifi_pass"] = "";
  doc["api_url"]   = "";
  doc["token"]     = "";

  File f = LittleFS.open(CONFIG_PATH, "w");
  if (!f) {
    Serial.println("ERROR: cannot create config.json");
    return;
  }
  serializeJson(doc, f);
  f.close();

  Serial.println("Created default /config.json");
}

static bool loadConfig() {
  if (!LittleFS.exists(CONFIG_PATH)) {
    Serial.println("Config missing");
    return false;
  }

  File f = LittleFS.open(CONFIG_PATH, "r");
  if (!f) {
    Serial.println("ERROR: cannot open config.json");
    return false;
  }

  StaticJsonDocument<512> doc;
  DeserializationError err = deserializeJson(doc, f);
  f.close();

  if (err) {
    Serial.print("ERROR: JSON parse failed: ");
    Serial.println(err.c_str());
    return false;
  }

  WIFI_SSID = doc["wifi_ssid"].as<const char*>() ? doc["wifi_ssid"].as<const char*>() : "";
  WIFI_PASS = doc["wifi_pass"].as<const char*>() ? doc["wifi_pass"].as<const char*>() : "";
  API_URL   = doc["api_url"].as<const char*>()   ? doc["api_url"].as<const char*>()   : "";
  TOKEN     = doc["token"].as<const char*>()     ? doc["token"].as<const char*>()     : "";

  Serial.println("Loaded config:");
  Serial.print("  wifi_ssid: "); Serial.println(WIFI_SSID);
  Serial.print("  api_url:   "); Serial.println(API_URL);

  return true;
}

static void saveConfigNow(const String& ssid, const String& pass, const String& api, const String& token) {
  StaticJsonDocument<512> doc;
  doc["wifi_ssid"] = ssid;
  doc["wifi_pass"] = pass;
  doc["api_url"]   = api;
  doc["token"]     = token;

  File f = LittleFS.open(CONFIG_PATH, "w");
  if (!f) {
    Serial.println("ERROR: cannot write config.json");
    return;
  }
  serializeJson(doc, f);
  f.close();

  WIFI_SSID = ssid;
  WIFI_PASS = pass;
  API_URL   = api;
  TOKEN     = token;

  Serial.println("Config saved!");
}

// ==================== SETUP PORTAL ====================
static void startSetupPortal() {
  Serial.println("Starting SETUP AP...");

  WiFi.mode(WIFI_AP);

  IPAddress apIP(192, 168, 4, 1);
  IPAddress apGW(192, 168, 4, 1);
  IPAddress apSN(255, 255, 255, 0);

  WiFi.softAPConfig(apIP, apGW, apSN);
  WiFi.softAP(SETUP_AP_SSID, SETUP_AP_PASS);

  dnsServer.start(DNS_PORT, "*", WiFi.softAPIP());

  server.onNotFound([]() {
    server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString(), true);
    server.send(302, "text/plain", "");
  });

  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());

  server.on("/", HTTP_GET, []() {
    String page =
      "<!doctype html>"
      "<html lang='en'>"
      "<head>"
      "  <meta charset='utf-8'/>"
      "  <meta name='viewport' content='width=device-width, initial-scale=1'/>"
      "  <title>FreeClass Setup</title>"
      "  <style>"
      "    *{box-sizing:border-box}"
      "    body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:#f4f6f8;color:#222;}"
      "    .container{max-width:420px;margin:40px auto;background:#fff;border-radius:14px;padding:24px;box-shadow:0 10px 30px rgba(0,0,0,0.08);}"
      "    h2{margin-top:0;text-align:center;font-size:22px;}"
      "    p.subtitle{text-align:center;color:#666;font-size:14px;margin-bottom:24px;}"
      "    label{display:block;margin-top:14px;font-size:14px;font-weight:600;}"
      "    input{width:100%;padding:12px;margin-top:6px;border-radius:8px;border:1px solid #ccc;font-size:15px;}"
      "    input:focus{outline:none;border-color:#3b82f6;}"
      "    button{width:100%;margin-top:24px;padding:14px;font-size:16px;font-weight:600;border:none;border-radius:10px;background:#3b82f6;color:#fff;cursor:pointer;}"
      "    button:hover{background:#2563eb}"
      "    .note{margin-top:18px;font-size:13px;color:#666;text-align:center;}"
      "  </style>"
      "</head>"
      "<body>"
      "  <div class='container'>"
      "    <h2>FreeClass Sensor Setup</h2>"
      "    <p class='subtitle'>Configure your sensor to get started</p>"
      "    <form method='POST' action='/save'>"
      "      <label>Wi-Fi Network Name (SSID)</label>"
      "      <input name='ssid' placeholder='MyWiFi' value='" + htmlEscape(WIFI_SSID) + "'/>"
      "      <label>Wi-Fi Password</label>"
      "      <input name='pass' type='password' placeholder='••••••••' value='" + htmlEscape(WIFI_PASS) + "'/>"
      "      <label>API URL</label>"
      "      <input name='api' placeholder='https://example.com/api' value='" + htmlEscape(API_URL) + "'/>"
      "      <label>Private Key</label>"
      "      <input name='token' placeholder='Paste your key here' value='" + htmlEscape(TOKEN) + "'/>"
      "      <button type='submit'>Save & Restart</button>"
      "    </form>"
      "    <div class='note'>The device will restart automatically after saving</div>"
      "  </div>"
      "</body>"
      "</html>";

    server.send(200, "text/html", page);
  });

  server.on("/save", HTTP_POST, []() {
    String ssid  = server.arg("ssid");
    String pass  = server.arg("pass");
    String api   = server.arg("api");
    String token = server.arg("token");

    saveConfigNow(ssid, pass, api, token);

    server.send(200, "text/html",
      "<!doctype html><html><head><meta charset='utf-8'/>"
      "<meta name='viewport' content='width=device-width,initial-scale=1'/>"
      "<title>Saved</title></head><body>"
      "<h3>Saved ✅</h3><p>Restarting...</p></body></html>"
    );

    delay(800);
    ESP.restart();
  });

  server.begin();
  Serial.println("Setup portal ready: open http://192.168.4.1");
}

// =====================================================
// SETUP / LOOP
// =====================================================
void setup() {
  Serial.begin(115200);

  // BOOT pin configured immediately (even if we go to portal)
  pinMode(RESET_BTN_PIN, INPUT_PULLUP);

  if (!LittleFS.begin(true)) {
    Serial.println("LittleFS begin FAILED");
  }

  writeDefaultConfigIfMissing();
  loadConfig();

  pinMode(LED_PIN, OUTPUT);
  ledOffHard();
  setLedMode(LedMode::OFF);

  // If missing config -> setup portal
  if (WIFI_SSID.length() == 0 || WIFI_PASS.length() == 0 || API_URL.length() == 0 || TOKEN.length() == 0) {
    startSetupPortal();
    return;
  }

  pinMode(PIR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIR_PIN), onPirRise, RISING);

  ensureWiFiConnected(); // now has timeout + reset check inside

  occupied = false;
  lastMotionMs = millis();
  ledOffHard();
}

void loop() {
  // ✅ reset check ALWAYS (works in all modes)
  checkDevLongPressReset();

  // Setup portal mode
  if (WiFi.getMode() == WIFI_AP) {
    // reset check also here (so it works while portal is open)
    checkDevLongPressReset();
    dnsServer.processNextRequest();
    server.handleClient();
    delay(5);
    return;
  }

  const unsigned long now = millis();

  if (ledMode == LedMode::OFF) ledOffHard();

  if (WiFi.status() != WL_CONNECTED) {
    requestInFlight = false;
    ensureWiFiConnected(); // has timeout + reset check inside
    ledOffHard();
    // if ensureWiFiConnected() switched to AP, next loop will handle it
  }

  // Consume interrupt flag
  bool edge = false;
  unsigned long edgeAt = 0;
  if (pirEdgeSeen) {
    noInterrupts();
    edge = pirEdgeSeen;
    edgeAt = pirEdgeMs;
    pirEdgeSeen = false;
    interrupts();
  }

  bool motionDetected = false;

  if (edge) {
    delay(5);
    if (digitalRead(PIR_PIN) == HIGH) {
      motionDetected = readStableHigh(HIGH_STABLE_MS);
    }
    if (motionDetected) {
      Serial.print("Motion confirmed at ms=");
      Serial.println(edgeAt);
    }
  }

  if (motionDetected) lastMotionMs = now;

  bool shouldBeOccupied = occupied;
  if (!occupied && motionDetected) shouldBeOccupied = true;
  else if (occupied && (now - lastMotionMs >= UNOCCUPIED_AFTER_MS)) shouldBeOccupied = false;

  const bool needSend = (!occupied && shouldBeOccupied);

  if (motionDetected && !requestInFlight) {
    if (needSend) {
      requestInFlight = true;
      setLedMode(LedMode::SOLID_ON);
      (void)sendOccupiedEvent();
      setLedMode(LedMode::OFF);
      ledOffHard();
      requestInFlight = false;
    } else {
      setLedMode(LedMode::MOTION_BLINK_WINDOW);
      motionBlinkUntilMs = now + MOTION_BLINK_WINDOW_MS;
    }
  }

  occupied = shouldBeOccupied;

  updateLed();
  delay(10);
}
