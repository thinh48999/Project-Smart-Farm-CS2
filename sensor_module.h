/*
 * sensor_module.h
 * Module đọc PIR, Flame, MQ2, LDR
 */

#ifndef SENSOR_MODULE_H
#define SENSOR_MODULE_H

#include <Arduino.h>

// Callback cho PIR
typedef void (*PIRCallback)();

void sensorInit();
void sensorUpdate();  // Gọi trong loop
void sensorSetPIRCallback(PIRCallback cb);

// PIR
bool sensorPIRDetected();

// Flame
bool sensorFlameDetected();

// MQ2 (digital)
bool sensorGasDetected();

// LDR (digital)
bool sensorIsDark();

#endif