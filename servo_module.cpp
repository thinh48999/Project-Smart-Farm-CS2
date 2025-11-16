/*
 * servo_module.cpp
 * Module điều khiển 2 Servo (Gate + Door)
 */

#include "servo_module.h"
#include "PIN_MAPPING_MEGA_TIDY.h"
#include <Servo.h>

Servo servoGate;
Servo servoDoor;

bool gateOpen = false;
bool doorOpen = false;
unsigned long gateOpenTime = 0;
unsigned long doorOpenTime = 0;

void servoInit() {
  servoGate.attach(SERVO_GATE_PIN);
  servoDoor.attach(SERVO_DOOR_PIN);
  servoGate.write(SERVO_GATE_CLOSE);
  servoDoor.write(SERVO_DOOR_CLOSE);
}

void servoUpdate() {
  unsigned long now = millis();
  
  // Tự động đóng cổng sau SERVO_DELAY
  if (gateOpen && (now - gateOpenTime > SERVO_DELAY)) {
    servoGateClose();
  }
  
  // Tự động đóng cửa sau SERVO_DELAY
  if (doorOpen && (now - doorOpenTime > SERVO_DELAY)) {
    servoDoorClose();
  }
}

// ===== GATE =====
void servoGateOpen() {
  servoGate.write(SERVO_GATE_OPEN);
  gateOpen = true;
  gateOpenTime = millis();
}

void servoGateClose() {
  servoGate.write(SERVO_GATE_CLOSE);
  gateOpen = false;
}

void servoGateToggle() {
  if (gateOpen) servoGateClose();
  else servoGateOpen();
}

bool servoGateIsOpen() {
  return gateOpen;
}

// ===== DOOR =====
void servoDoorOpen() {
  servoDoor.write(SERVO_DOOR_OPEN);
  doorOpen = true;
  doorOpenTime = millis();
}

void servoDoorClose() {
  servoDoor.write(SERVO_DOOR_CLOSE);
  doorOpen = false;
}

void servoDoorToggle() {
  if (doorOpen) servoDoorClose();
  else servoDoorOpen();
}

bool servoDoorIsOpen() {
  return doorOpen;
}