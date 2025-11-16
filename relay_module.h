/*
 * relay_module.h
 * Module điều khiển 3 Relay (Light, Fan, Pump)
 */

#ifndef RELAY_MODULE_H
#define RELAY_MODULE_H

#include <Arduino.h>

void relayInit();
void relayUpdate();  // Gọi trong loop để tự động tắt pump

// Light
void relayLightOn();
void relayLightOff();
void relayLightToggle();
bool relayLightIsOn();

// Fan
void relayFanOn();
void relayFanOff();
void relayFanToggle();
bool relayFanIsOn();

// Pump
void relayPumpOn();
void relayPumpOff();
void relayPumpToggle();
void relayPumpOnTimed(unsigned long duration);  // Bật có thời hạn
bool relayPumpIsOn();

#endif