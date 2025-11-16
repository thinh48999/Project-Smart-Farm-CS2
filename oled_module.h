/*
 * oled_module.h
 * Module hiển thị OLED SH1106
 * Sử dụng thư viện Adafruit_SH1106
 */

#ifndef OLED_MODULE_H
#define OLED_MODULE_H

#include <Arduino.h>

void oledInit();
void oledClear();
void oledUpdate(float temp, float humidity, String airQuality);
void oledDisplayMessage(String msg);
void oledDisplayFire();  // Hiển thị cảnh báo lửa
void oledDisplayGas();   // Hiển thị cảnh báo gas

#endif