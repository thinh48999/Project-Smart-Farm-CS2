/*
 * rfid_module.cpp
 */

#include "rfid_module.h"
#include "PIN_MAPPING_MEGA_TIDY.h"
#include <SPI.h>
#include <MFRC522.h>

MFRC522 mfrc522(RC522_SS_PIN, RC522_RST_PIN);

#define MAX_CARDS 10
byte validUIDs[MAX_CARDS][7];
byte uidLengths[MAX_CARDS];
int cardCount = 0;

RFIDCallback onCardScanned = nullptr;

bool lastCardAuthorized = false;
byte lastUID[7];
byte lastUIDLength = 0;
unsigned long lastScanTime = 0;
const unsigned long SCAN_DELAY = 2000;

void rfidInit() {
  SPI.begin();
  pinMode(RC522_SS_PIN, OUTPUT);
  pinMode(53, OUTPUT);
  
  mfrc522.PCD_Init();
  delay(10);
  
  Serial.println(F("RC522 init OK"));
  Serial.print(F("RC522 Version: 0x"));
  Serial.println(mfrc522.PCD_ReadRegister(mfrc522.VersionReg), HEX);
}

bool isValidUID(byte *uid, byte length) {
  for (int i = 0; i < cardCount; i++) {
    if (uidLengths[i] != length) continue;
    
    bool match = true;
    for (int j = 0; j < length; j++) {
      if (uid[j] != validUIDs[i][j]) {
        match = false;
        break;
      }
    }
    if (match) return true;
  }
  return false;
}

void rfidUpdate() {
  unsigned long now = millis();
  
  if (now - lastScanTime < SCAN_DELAY) return;
  
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;
  
  lastUIDLength = mfrc522.uid.size;
  for (byte i = 0; i < lastUIDLength; i++) {
    lastUID[i] = mfrc522.uid.uidByte[i];
  }
  lastScanTime = now;
  
  lastCardAuthorized = isValidUID(lastUID, lastUIDLength);
  
  Serial.print(F("📇 RFID "));
  Serial.print(lastUIDLength);
  Serial.print(F(" byte: "));
  for (byte i = 0; i < lastUIDLength; i++) {
    if (lastUID[i] < 0x10) Serial.print("0");
    Serial.print(lastUID[i], HEX);
    if (i < lastUIDLength - 1) Serial.print(" ");
  }
  Serial.print(F(" -> "));
  Serial.println(lastCardAuthorized ? F("✅ OK") : F("❌ DENIED"));
  
  if (onCardScanned) {
    onCardScanned(lastCardAuthorized);
  }
  
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void rfidAddCard4Byte(byte uid[4]) {
  if (cardCount >= MAX_CARDS) {
    Serial.println(F("Card list FULL!"));
    return;
  }
  
  for (byte i = 0; i < 4; i++) {
    validUIDs[cardCount][i] = uid[i];
  }
  uidLengths[cardCount] = 4;
  cardCount++;
  
  Serial.print(F("Added 4-byte card: "));
  for (byte i = 0; i < 4; i++) {
    if (uid[i] < 0x10) Serial.print("0");
    Serial.print(uid[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
}

void rfidAddCard7Byte(byte uid[7]) {
  if (cardCount >= MAX_CARDS) {
    Serial.println(F("Card list FULL!"));
    return;
  }
  
  for (byte i = 0; i < 7; i++) {
    validUIDs[cardCount][i] = uid[i];
  }
  uidLengths[cardCount] = 7;
  cardCount++;
  
  Serial.print(F("Added 7-byte card: "));
  for (byte i = 0; i < 7; i++) {
    if (uid[i] < 0x10) Serial.print("0");
    Serial.print(uid[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
}

int rfidGetCardCount() {
  return cardCount;
}

void rfidSetCallback(RFIDCallback cb) {
  onCardScanned = cb;
}

bool rfidWasLastCardAuthorized() {
  return lastCardAuthorized;
}

void rfidPrintLastUID() {
  Serial.print(F("Last UID: "));
  for (byte i = 0; i < lastUIDLength; i++) {
    if (lastUID[i] < 0x10) Serial.print("0");
    Serial.print(lastUID[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
}