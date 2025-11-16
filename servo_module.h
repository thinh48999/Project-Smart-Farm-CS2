/*
 * servo_module.h
 * Module điều khiển 2 Servo (Gate + Door)
 */

#ifndef SERVO_MODULE_H
#define SERVO_MODULE_H

#include <Arduino.h>

void servoInit();
void servoUpdate();  // Gọi trong loop để tự động đóng

// Gate
void servoGateOpen();
void servoGateClose();
void servoGateToggle();
bool servoGateIsOpen();

// Door
void servoDoorOpen();
void servoDoorClose();
void servoDoorToggle();
bool servoDoorIsOpen();

#endif