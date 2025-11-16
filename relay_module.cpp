/*
 * relay_module.cpp
 * Module điều khiển 3 Relay (Light, Fan, Pump)
 */

#include "relay_module.h"
#include "PIN_MAPPING_MEGA_TIDY.h"

bool lightState = false;
bool fanState = false;
bool pumpState = false;
unsigned long pumpStartTime = 0;
unsigned long pumpDuration = 0;

void relayInit() {
  pinMode(RELAY_LIGHT, OUTPUT);
  pinMode(RELAY_FAN, OUTPUT);
  pinMode(RELAY_PUMP, OUTPUT);
  digitalWrite(RELAY_LIGHT, LOW);
  digitalWrite(RELAY_FAN, LOW);
  digitalWrite(RELAY_PUMP, LOW);
}

void relayUpdate() {
  // Tự động tắt pump sau khoảng thời gian
  if (pumpState && pumpDuration > 0) {
    if (millis() - pumpStartTime >= pumpDuration) {
      relayPumpOff();
      pumpDuration = 0;
    }
  }
}

// ===== LIGHT =====
void relayLightOn() {
  digitalWrite(RELAY_LIGHT, HIGH);
  lightState = true;
}

void relayLightOff() {
  digitalWrite(RELAY_LIGHT, LOW);
  lightState = false;
}

void relayLightToggle() {
  if (lightState) relayLightOff();
  else relayLightOn();
}

bool relayLightIsOn() {
  return lightState;
}

// ===== FAN =====
void relayFanOn() {
  digitalWrite(RELAY_FAN, HIGH);
  fanState = true;
}

void relayFanOff() {
  digitalWrite(RELAY_FAN, LOW);
  fanState = false;
}

void relayFanToggle() {
  if (fanState) relayFanOff();
  else relayFanOn();
}

bool relayFanIsOn() {
  return fanState;
}

// ===== PUMP =====
void relayPumpOn() {
  digitalWrite(RELAY_PUMP, HIGH);
  pumpState = true;
}

void relayPumpOff() {
  digitalWrite(RELAY_PUMP, LOW);
  pumpState = false;
}

void relayPumpToggle() {
  if (pumpState) relayPumpOff();
  else relayPumpOn();
}

void relayPumpOnTimed(unsigned long duration) {
  relayPumpOn();
  pumpStartTime = millis();
  pumpDuration = duration;
}

bool relayPumpIsOn() {
  return pumpState;
}