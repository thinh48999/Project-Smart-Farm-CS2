/*
 * serial_command.cpp
 * Xử lý lệnh Serial từ GUI Python
 * 
 * Format lệnh: COMMAND:PARAM
 * Ví dụ:
 *   MODE:AUTO          -> Chuyển sang chế độ tự động
 *   MODE:MANUAL        -> Chuyển sang chế độ thủ công
 *   FAN:ON             -> Bật quạt (manual)
 *   PUMP:ON            -> Bật bơm (manual)
 *   GATE:OPEN          -> Mở cổng
 *   GET:ALL            -> Lấy tất cả dữ liệu
 */

#include "serial_command.h"
#include "system_mode.h"
#include "relay_module.h"
#include "servo_module.h"
#include "dht_module.h"
#include "sensor_module.h"
#include "rfid_module.h"

void serialCommandInit() {
  Serial.println(F("╔════════════════════════════════════════╗"));
  Serial.println(F("║   SERIAL COMMAND READY                ║"));
  Serial.println(F("╚════════════════════════════════════════╝"));
  Serial.println(F("Commands:"));
  Serial.println(F("  MODE:AUTO / MODE:MANUAL"));
  Serial.println(F("  FAN:ON / FAN:OFF / FAN:TOGGLE"));
  Serial.println(F("  PUMP:ON / PUMP:OFF"));
  Serial.println(F("  LIGHT:ON / LIGHT:OFF"));
  Serial.println(F("  GATE:OPEN / GATE:CLOSE"));
  Serial.println(F("  DOOR:OPEN / DOOR:CLOSE"));
  Serial.println(F("  GET:ALL / GET:TEMP / GET:HUMIDITY"));
  Serial.println(F("  AUTOFAN:ON / AUTOFAN:OFF"));
  Serial.println(F("  AUTOPUMP:ON / AUTOPUMP:OFF"));
  Serial.println(F("  AUTOLIGHT:ON / AUTOLIGHT:OFF"));
}

void serialCommandUpdate() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();
    
    int colonIndex = cmd.indexOf(':');
    if (colonIndex > 0) {
      String command = cmd.substring(0, colonIndex);
      String param = cmd.substring(colonIndex + 1);
      
      // ===== MODE CONTROL =====
      if (command == "MODE") {
        if (param == "AUTO") {
          setSystemMode(MODE_AUTO);
          Serial.println(F("OK:MODE:AUTO"));
        } else if (param == "MANUAL") {
          setSystemMode(MODE_MANUAL);
          Serial.println(F("OK:MODE:MANUAL"));
        }
      }
      
      // ===== AUTO ENABLE/DISABLE =====
      else if (command == "AUTOFAN") {
        setAutoFan(param == "ON");
        Serial.print(F("OK:AUTOFAN:"));
        Serial.println(param);
      }
      else if (command == "AUTOPUMP") {
        setAutoPump(param == "ON");
        Serial.print(F("OK:AUTOPUMP:"));
        Serial.println(param);
      }
      else if (command == "AUTOLIGHT") {
        setAutoLight(param == "ON");
        Serial.print(F("OK:AUTOLIGHT:"));
        Serial.println(param);
      }
      
      // ===== RELAY CONTROL (MANUAL MODE) =====
      else if (command == "FAN") {
        if (isManualMode()) {
          if (param == "ON") relayFanOn();
          else if (param == "OFF") relayFanOff();
          else if (param == "TOGGLE") relayFanToggle();
          Serial.print(F("OK:FAN:"));
          Serial.println(relayFanIsOn() ? F("ON") : F("OFF"));
        } else {
          Serial.println(F("ERROR:MANUAL_MODE_REQUIRED"));
        }
      }
      else if (command == "PUMP") {
        if (isManualMode()) {
          if (param == "ON") relayPumpOn();
          else if (param == "OFF") relayPumpOff();
          Serial.print(F("OK:PUMP:"));
          Serial.println(relayPumpIsOn() ? F("ON") : F("OFF"));
        } else {
          Serial.println(F("ERROR:MANUAL_MODE_REQUIRED"));
        }
      }
      else if (command == "LIGHT") {
        if (isManualMode()) {
          if (param == "ON") relayLightOn();
          else if (param == "OFF") relayLightOff();
          Serial.print(F("OK:LIGHT:"));
          Serial.println(relayLightIsOn() ? F("ON") : F("OFF"));
        } else {
          Serial.println(F("ERROR:MANUAL_MODE_REQUIRED"));
        }
      }
      
      // ===== SERVO CONTROL =====
      else if (command == "GATE") {
        if (param == "OPEN") servoGateOpen();
        else if (param == "CLOSE") servoGateClose();
        Serial.print(F("OK:GATE:"));
        Serial.println(servoGateIsOpen() ? F("OPEN") : F("CLOSED"));
      }
      else if (command == "DOOR") {
        if (param == "OPEN") servoDoorOpen();
        else if (param == "CLOSE") servoDoorClose();
        Serial.print(F("OK:DOOR:"));
        Serial.println(servoDoorIsOpen() ? F("OPEN") : F("CLOSED"));
      }
      
      // ===== GET SENSOR DATA =====
      else if (command == "GET") {
        if (param == "TEMP") {
          Serial.print(F("DATA:TEMP:"));
          Serial.println(dhtGetTemperature(), 1);
        }
        else if (param == "HUMIDITY") {
          Serial.print(F("DATA:HUMIDITY:"));
          Serial.println(dhtGetHumidity(), 1);
        }
        else if (param == "ALL") {
          // JSON format
          Serial.print(F("DATA:ALL:{"));
          Serial.print(F("\"mode\":\""));
          Serial.print(isAutoMode() ? F("AUTO") : F("MANUAL"));
          Serial.print(F("\",\"temp\":"));
          Serial.print(dhtGetTemperature(), 1);
          Serial.print(F(",\"humidity\":"));
          Serial.print(dhtGetHumidity(), 1);
          Serial.print(F(",\"gas\":"));
          Serial.print(sensorGasDetected() ? 1 : 0);
          Serial.print(F(",\"flame\":"));
          Serial.print(sensorFlameDetected() ? 1 : 0);
          Serial.print(F(",\"dark\":"));
          Serial.print(sensorIsDark() ? 1 : 0);
          Serial.print(F(",\"fan\":"));
          Serial.print(relayFanIsOn() ? 1 : 0);
          Serial.print(F(",\"pump\":"));
          Serial.print(relayPumpIsOn() ? 1 : 0);
          Serial.print(F(",\"light\":"));
          Serial.print(relayLightIsOn() ? 1 : 0);
          Serial.print(F(",\"gate\":"));
          Serial.print(servoGateIsOpen() ? 1 : 0);
          Serial.print(F(",\"door\":"));
          Serial.print(servoDoorIsOpen() ? 1 : 0);
          Serial.println(F("}"));
        }
      }
      
      else {
        Serial.println(F("ERROR:UNKNOWN_COMMAND"));
      }
    }
  }
}