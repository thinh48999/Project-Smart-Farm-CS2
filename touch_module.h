/*
 * touch_module.h
 * Module xử lý 4 nút Touch (Gate, Fan, Door, Pump)
 */

#ifndef TOUCH_MODULE_H
#define TOUCH_MODULE_H

#include <Arduino.h>

// Callback functions - bạn sẽ định nghĩa trong main
typedef void (*TouchCallback)();

void touchInit();
void touchUpdate();  // Gọi trong loop

void touchSetGateCallback(TouchCallback cb);
void touchSetFanCallback(TouchCallback cb);
void touchSetDoorCallback(TouchCallback cb);
void touchSetPumpCallback(TouchCallback cb);

#endif