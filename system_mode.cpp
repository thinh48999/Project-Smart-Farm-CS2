/*
 * system_mode.cpp
 * Quản lý chế độ Auto/Manual
 */

#include "system_mode.h"

SystemMode currentMode = MODE_AUTO;  // Mặc định là Auto
bool autoFanEnabled = true;
bool autoPumpEnabled = true;
bool autoLightEnabled = true;

void systemModeInit() {
  currentMode = MODE_AUTO;
  Serial.println(F("System Mode: AUTO"));
}

void setSystemMode(SystemMode mode) {
  currentMode = mode;
  if (mode == MODE_AUTO) {
    Serial.println(F("Switched to AUTO mode"));
  } else {
    Serial.println(F("Switched to MANUAL mode"));
  }
}

SystemMode getSystemMode() {
  return currentMode;
}

bool isAutoMode() {
  return currentMode == MODE_AUTO;
}

bool isManualMode() {
  return currentMode == MODE_MANUAL;
}

void setAutoFan(bool enable) {
  autoFanEnabled = enable;
  Serial.print(F("Auto Fan: "));
  Serial.println(enable ? F("ON") : F("OFF"));
}

void setAutoPump(bool enable) {
  autoPumpEnabled = enable;
  Serial.print(F("Auto Pump: "));
  Serial.println(enable ? F("ON") : F("OFF"));
}

void setAutoLight(bool enable) {
  autoLightEnabled = enable;
  Serial.print(F("Auto Light: "));
  Serial.println(enable ? F("ON") : F("OFF"));
}

bool isAutoFanEnabled() {
  return autoFanEnabled && isAutoMode();
}

bool isAutoPumpEnabled() {
  return autoPumpEnabled && isAutoMode();
}

bool isAutoLightEnabled() {
  return autoLightEnabled && isAutoMode();
}