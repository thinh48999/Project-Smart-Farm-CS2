/*
 * SmartFarm.ino
 * Hệ thống Smart Farm Hoàn Chỉnh
 * Auto/Manual Mode + GUI Python Support
 * Author: LeHoangNhuan
 * Date: 2025-11-14
 */

#include "PIN_MAPPING_MEGA_TIDY.h"
#include "buzzer_module.h"
#include "dht_module.h"
#include "servo_module.h"
#include "relay_module.h"
#include "touch_module.h"
#include "sensor_module.h"
#include "oled_module.h"
#include "rfid_module.h"
#include "system_mode.h"
#include "serial_command.h"

unsigned long lastSensorRead = 0;
unsigned long lastOledUpdate = 0;
unsigned long lastAutoReport = 0;
bool fireAlertActive = false;
bool gasAlertActive = false;

// ===== CALLBACK: RFID + Touch Gate =====
void onRFIDScanned(bool authorized) {
  if (authorized) {
    Serial.println(F("✅ Valid Card - Opening Gate"));
    servoGateOpen();
    buzzerBeep(1);  // 1 beep
    oledDisplayMessage("Gate OPEN\nAccess OK");
    delay(1500);
  } else {
    Serial.println(F("❌ Invalid Card"));
    buzzerBeep(5);  // 5 beeps
    oledDisplayMessage("Access DENIED");
    delay(1500);
  }
}

void onTouchGate() {
  Serial.println(F("👆 Touch: GATE"));
  servoGateToggle();
  buzzerBeep(1);
}

// ===== CALLBACK: PIR + Touch Door =====
void onPIRMotion() {
  Serial.println(F("🚶 PIR: Motion detected!"));
  servoDoorOpen();
}

void onTouchDoor() {
  Serial.println(F("👆 Touch: DOOR"));
  servoDoorToggle();
}

// ===== CALLBACK: Touch Fan/Pump =====
void onTouchFan() {
  Serial.println(F("👆 Touch: FAN"));
  relayFanToggle();
  buzzerBeep(1);
}

void onTouchPump() {
  Serial.println(F("👆 Touch: PUMP"));
  relayPumpOnTimed(5000);  // 5 giây
  buzzerBeep(1);
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println(F("╔═══════════════════════════════════════╗"));
  Serial.println(F("║   SMART FARM COMPLETE SYSTEM         ║"));
  Serial.println(F("║   Auto/Manual Mode                   ║"));
  Serial.println(F("║   Author: LeHoangNhuan               ║"));
  Serial.println(F("║   Date: 2025-11-14                   ║"));
  Serial.println(F("╚═══════════════════════════════════════╝"));
  
  // Khởi tạo modules
  buzzerInit();
  dhtInit();
  servoInit();
  relayInit();
  touchInit();
  sensorInit();
  oledInit();
  rfidInit();
  systemModeInit();
  serialCommandInit();
  
  // Đăng ký callbacks
  rfidSetCallback(onRFIDScanned);
  touchSetGateCallback(onTouchGate);
  touchSetFanCallback(onTouchFan);
  touchSetDoorCallback(onTouchDoor);
  touchSetPumpCallback(onTouchPump);
  sensorSetPIRCallback(onPIRMotion);
  
  // Thêm thẻ RFID hợp lệ
  byte card1[4] = {0x2E, 0xE1, 0xCC, 0x05};
  byte card2[7] = {0x04, 0xE5, 0x78, 0xA2, 0x54, 0x6C, 0x80};
  rfidAddCard4Byte(card1);
  rfidAddCard7Byte(card2);
  
  buzzerBeep(2);
  Serial.println(F("\n✅ System Ready!"));
  Serial.print(F("Cards loaded: "));
  Serial.println(rfidGetCardCount());
  Serial.println();
}

// ===== LOOP =====
void loop() {
  unsigned long now = millis();
  
  // Đọc cảm biến mỗi 2s
  if (now - lastSensorRead >= SENSOR_UPDATE) {
    lastSensorRead = now;
    readSensors();
    checkAlerts();
    
    // Chỉ auto control khi ở chế độ AUTO
    if (isAutoMode()) {
      autoControl();
    }
  }
  
  // Cập nhật OLED mỗi 3s
  if (now - lastOledUpdate >= OLED_UPDATE) {
    lastOledUpdate = now;
    if (!fireAlertActive && !gasAlertActive) {
      updateDisplay();
    }
  }
  
  // Auto report cho GUI mỗi 5s
  if (now - lastAutoReport >= 5000) {
    lastAutoReport = now;
    sendAutoReport();
  }
  
  // Cập nhật modules
  serialCommandUpdate();  // Xử lý lệnh Serial
  touchUpdate();
  sensorUpdate();
  servoUpdate();
  relayUpdate();
  rfidUpdate();
  
  delay(10);
}

// ===== ĐỌC CẢM BIẾN =====
void readSensors() {
  dhtRead();
  
  if (dhtIsValid()) {
    Serial.print(F("[Sensor] T="));
    Serial.print(dhtGetTemperature(), 1);
    Serial.print(F("°C, H="));
    Serial.print(dhtGetHumidity(), 1);
    Serial.print(F("%"));
  } else {
    Serial.print(F("[Sensor] DHT Error"));
  }
  
  if (sensorGasDetected()) Serial.print(F(" | GAS!"));
  if (sensorFlameDetected()) Serial.print(F(" | FIRE!"));
  if (sensorIsDark()) Serial.print(F(" | DARK"));
  
  Serial.println();
}

// ===== KIỂM TRA CẢNH BÁO =====
void checkAlerts() {
  // Cảnh báo lửa
  if (sensorFlameDetected() && !fireAlertActive) {
    fireAlertActive = true;
    Serial.println(F("\n🔥 FIRE ALERT!"));
    
    relayLightOff();
    relayFanOff();
    relayPumpOff();
    servoGateOpen();
    servoDoorOpen();
    
    oledDisplayFire();
    buzzerPattern();  // Buzzer thụ động
    
  } else if (!sensorFlameDetected()) {
    fireAlertActive = false;
  }
  
  // Cảnh báo gas
  if (sensorGasDetected() && !gasAlertActive) {
    gasAlertActive = true;
    Serial.println(F("\n⚠ GAS WARNING!"));
    oledDisplayGas();
    buzzerPattern();  // Buzzer thụ động
  } else if (!sensorGasDetected()) {
    gasAlertActive = false;
  }
}

// ===== ĐIỀU KHIỂN TỰ ĐỘNG (CHỈ KHI Ở CHẾ ĐỘ AUTO) =====
void autoControl() {
  // Không auto khi có cảnh báo lửa
  if (fireAlertActive) return;
  
  // Auto Fan theo nhiệt độ
  if (isAutoFanEnabled()) {
    if (dhtGetTemperature() > 35.0 && !relayFanIsOn()) {
      relayFanOn();
      Serial.println(F("  → [AUTO] Fan ON (T>35°C)"));
    } else if (dhtGetTemperature() <= 33.0 && relayFanIsOn()) {
      relayFanOff();
      Serial.println(F("  → [AUTO] Fan OFF (T≤33°C)"));
    }
  }
  
  // Auto Light theo LDR
  if (isAutoLightEnabled()) {
    if (sensorIsDark() && !relayLightIsOn()) {
      relayLightOn();
      Serial.println(F("  → [AUTO] Light ON (Dark)"));
    } else if (!sensorIsDark() && relayLightIsOn()) {
      relayLightOff();
      Serial.println(F("  → [AUTO] Light OFF (Bright)"));
    }
  }
  
  // Auto Pump theo độ ẩm
  if (isAutoPumpEnabled()) {
    if (dhtGetHumidity() < 50.0 && !relayPumpIsOn()) {
      relayPumpOnTimed(5000);  // 5 giây
      Serial.println(F("  → [AUTO] Pump ON 5s (H<50%)"));
    }
  }
}

// ===== CẬP NHẬT OLED =====
void updateDisplay() {
  String airQuality = (sensorGasDetected() || sensorFlameDetected()) ? "DNGR" : "GOOD";
  oledUpdate(dhtGetTemperature(), dhtGetHumidity(), airQuality);
}

// ===== GỬI DỮ LIỆU CHO GUI (Auto Report) =====
// ===== Gửi Dữ Liệu cho GUI (Auto Report) =====
void sendAutoReport() {
  Serial.print(F("REPORT:{"));
  Serial.print(F("\"mode\":\""));
  Serial.print(isAutoMode() ? F("AUTO") : F("MANUAL"));
  Serial.print(F("\",\"temp\":"));
  Serial.print(dhtGetTemperature(), 1);
  Serial.print(F(",\"hum\":"));
  Serial.print(dhtGetHumidity(), 1);
  
  // ✅ THÊM ĐẦY ĐỦ CÁC SENSOR
  Serial.print(F(",\"gas\":"));
  Serial.print(sensorGasDetected() ? 1 : 0);
  Serial.print(F(",\"flame\":"));
  Serial.print(sensorFlameDetected() ? 1 : 0);
  Serial.print(F(",\"dark\":"));
  Serial.print(sensorIsDark() ? 1 : 0);
  
  Serial.print(F(",\"fan\":"));
  Serial.print(relayFanIsOn() ? 1 : 0);
  Serial.print(F(",\"pump\":"));
  Serial.print(relayPumpIsOn() ? 1 : 0);
  Serial.print(F(",\"light\":"));
  Serial.print(relayLightIsOn() ? 1 : 0);
  
  // ✅ THÊM TRẠNG THÁI SERVO
  Serial.print(F(",\"gate\":"));
  Serial.print(servoGateIsOpen() ? 1 : 0);
  Serial.print(F(",\"door\":"));
  Serial.print(servoDoorIsOpen() ? 1 : 0);
  
  Serial.println(F("}"));
}