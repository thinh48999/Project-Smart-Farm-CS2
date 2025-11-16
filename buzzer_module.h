/*
 * buzzer_module.h
 * Module điều khiển Buzzer
 */

#ifndef BUZZER_MODULE_H
#define BUZZER_MODULE_H

#include <Arduino.h>

void buzzerInit();
void buzzerBeep(int times = 1);
void buzzerShortBeep();
void buzzerLongBeep();
void buzzerPattern();  // 3 ngắn + 1 dài
void buzzerTone(unsigned int freq, unsigned int duration);

#endif