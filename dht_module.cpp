/*
 * dht_module.cpp
 * Module đọc cảm biến DHT11
 */

#include "dht_module.h"
#include "PIN_MAPPING_MEGA_TIDY.h"
#include <DHT.h>

DHT dht(DHT_PIN, DHT11);
float temperature = 0;
float humidity = 0;
bool validReading = false;

void dhtInit() {
  dht.begin();
}

void dhtRead() {
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  
  if (!isnan(t) && !isnan(h)) {
    temperature = t;
    humidity = h;
    validReading = true;
  } else {
    validReading = false;
  }
}

float dhtGetTemperature() {
  return temperature;
}

float dhtGetHumidity() {
  return humidity;
}

bool dhtIsValid() {
  return validReading;
}