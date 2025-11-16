/*
 * rfid_module.h
 * Module RFID RC522
 */

#ifndef RFID_MODULE_H
#define RFID_MODULE_H

#include <Arduino.h>

typedef void (*RFIDCallback)(bool authorized);

void rfidInit();
void rfidUpdate();

void rfidAddCard4Byte(byte uid[4]);
void rfidAddCard7Byte(byte uid[7]);
int rfidGetCardCount();

void rfidSetCallback(RFIDCallback cb);

bool rfidWasLastCardAuthorized();
void rfidPrintLastUID();

#endif