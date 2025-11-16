/*
 * sensor_module.cpp
 * Module đọc PIR, Flame, MQ2, LDR
 */

#include "sensor_module.h"
#include "PIN_MAPPING_MEGA_TIDY.h"

PIRCallback pirCallback = nullptr;
bool lastPIRState = false;

void sensorInit() {
  pinMode(PIR_PIN, INPUT);
  pinMode(FLAME_PIN, INPUT);
  pinMode(MQ2_DOUT_PIN, INPUT);
  pinMode(LDR_DOUT_PIN, INPUT);
}

void sensorUpdate() {
  // Kiểm tra PIR (phát hiện chuyển động)
  bool currentPIR = digitalRead(PIR_PIN);
  if (currentPIR == HIGH && lastPIRState == LOW) {
    if (pirCallback) pirCallback();
  }
  lastPIRState = currentPIR;
}

void sensorSetPIRCallback(PIRCallback cb) {
  pirCallback = cb;
}

bool sensorPIRDetected() {
  return digitalRead(PIR_PIN) == HIGH;
}

bool sensorFlameDetected() {
  return digitalRead(FLAME_PIN) == LOW;  // Tùy module
}

bool sensorGasDetected() {
  return digitalRead(MQ2_DOUT_PIN) == HIGH;  // Tùy module
}

bool sensorIsDark() {
  return digitalRead(LDR_DOUT_PIN) == HIGH;  // Tùy module
}