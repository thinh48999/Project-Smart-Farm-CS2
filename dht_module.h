/*
 * dht_module.h
 * Module đọc cảm biến DHT11
 */

#ifndef DHT_MODULE_H
#define DHT_MODULE_H

#include <Arduino.h>

void dhtInit();
void dhtRead();
float dhtGetTemperature();
float dhtGetHumidity();
bool dhtIsValid();

#endif