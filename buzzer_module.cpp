/*
 * buzzer_module.cpp
 * Module điều khiển Buzzer
 */

#include "buzzer_module.h"
#include "PIN_MAPPING_MEGA_TIDY.h"

void buzzerInit() {
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
}

void buzzerBeep(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(BUZZER_DURATION / 2);
    digitalWrite(BUZZER_PIN, LOW);
    delay(BUZZER_DURATION / 2);
  }
}

void buzzerShortBeep() {
  tone(BUZZER_PIN, 2200);
  delay(120);
  noTone(BUZZER_PIN);
  delay(60);
}

void buzzerLongBeep() {
  tone(BUZZER_PIN, 1500);
  delay(450);
  noTone(BUZZER_PIN);
  delay(60);
}

void buzzerPattern() {
  for (int i = 0; i < 3; i++) buzzerShortBeep();
  delay(120);
  buzzerLongBeep();
}

void buzzerTone(unsigned int freq, unsigned int duration) {
  tone(BUZZER_PIN, freq);
  delay(duration);
  noTone(BUZZER_PIN);
}