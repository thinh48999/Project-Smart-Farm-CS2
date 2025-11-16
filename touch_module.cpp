/*
 * touch_module.cpp
 * Module xử lý 4 nút Touch (Gate, Fan, Door, Pump)
 */

#include "touch_module.h"
#include "PIN_MAPPING_MEGA_TIDY.h"

TouchCallback gateCallback = nullptr;
TouchCallback fanCallback = nullptr;
TouchCallback doorCallback = nullptr;
TouchCallback pumpCallback = nullptr;

unsigned long lastTouchGate = 0;
unsigned long lastTouchFan = 0;
unsigned long lastTouchDoor = 0;
unsigned long lastTouchPump = 0;

void touchInit() {
  pinMode(TOUCH_GATE_PIN, INPUT_PULLUP);
  pinMode(TOUCH_FAN_PIN, INPUT_PULLUP);
  pinMode(TOUCH_DOOR_PIN, INPUT_PULLUP);
  pinMode(TOUCH_PUMP_PIN, INPUT_PULLUP);
}

void touchUpdate() {
  unsigned long now = millis();
  
  // Touch Gate
  if (digitalRead(TOUCH_GATE_PIN) == LOW && (now - lastTouchGate > DEBOUNCE_DELAY)) {
    lastTouchGate = now;
    if (gateCallback) gateCallback();
  }
  
  // Touch Fan
  if (digitalRead(TOUCH_FAN_PIN) == LOW && (now - lastTouchFan > DEBOUNCE_DELAY)) {
    lastTouchFan = now;
    if (fanCallback) fanCallback();
  }
  
  // Touch Door
  if (digitalRead(TOUCH_DOOR_PIN) == LOW && (now - lastTouchDoor > DEBOUNCE_DELAY)) {
    lastTouchDoor = now;
    if (doorCallback) doorCallback();
  }
  
  // Touch Pump
  if (digitalRead(TOUCH_PUMP_PIN) == LOW && (now - lastTouchPump > DEBOUNCE_DELAY)) {
    lastTouchPump = now;
    if (pumpCallback) pumpCallback();
  }
}

void touchSetGateCallback(TouchCallback cb) { gateCallback = cb; }
void touchSetFanCallback(TouchCallback cb) { fanCallback = cb; }
void touchSetDoorCallback(TouchCallback cb) { doorCallback = cb; }
void touchSetPumpCallback(TouchCallback cb) { pumpCallback = cb; }