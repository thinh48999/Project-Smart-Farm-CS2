/*
 * oled_module.cpp
 * Module hiển thị OLED SH1106
 * Sử dụng thư viện Adafruit_SH1106
 */

#include "oled_module.h"
#include "PIN_MAPPING_MEGA_TIDY.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH1106.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET 4  // hoặc -1 nếu không có reset

Adafruit_SH1106 display(OLED_RESET);

void oledInit() {
  Wire.begin();
  display.begin(SH1106_SWITCHCAPVCC, OLED_ADDRESS); // 0x3C
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(F("Smart Farm"));
  display.println(F("System Ready"));
  display.display();
  delay(2000);
  Serial.println(F("OLED init OK"));
}

void oledClear() {
  display.clearDisplay();
  display.display();
}

void oledUpdate(float temp, float humidity, String airQuality) {
  display.clearDisplay();
  
  // Hiển thị nhiệt độ
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print(F("Temp: "));
  display.setTextSize(2);
  display.setCursor(0, 10);
  display.print(temp, 1);
  display.print((char)167); // ký hiệu độ °
  display.print(F("C"));
  
  // Hiển thị độ ẩm
  display.setTextSize(1);
  display.setCursor(0, 30);
  display.print(F("Humidity: "));
  display.setTextSize(2);
  display.setCursor(0, 40);
  display.print(humidity, 1);
  display.print(F("%"));
  
  // Hiển thị chất lượng không khí (nhỏ ở góc)
  display.setTextSize(1);
  display.setCursor(90, 0);
  display.print(airQuality);
  
  display.display();
}

void oledDisplayMessage(String msg) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println(msg);
  display.display();
}

void oledDisplayFire() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10, 10);
  display.print(F("FIRE!"));
  display.setTextSize(1);
  display.setCursor(10, 35);
  display.print(F("ALERT!!!"));
  display.display();
}

void oledDisplayGas() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10, 10);
  display.print(F("GAS!"));
  display.setTextSize(1);
  display.setCursor(10, 35);
  display.print(F("WARNING"));
  display.display();
}