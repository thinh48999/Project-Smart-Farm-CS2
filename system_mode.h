/*
 * system_mode.h
 * Quản lý chế độ Auto/Manual cho hệ thống
 */

#ifndef SYSTEM_MODE_H
#define SYSTEM_MODE_H

#include <Arduino.h>

// Chế độ hệ thống
enum SystemMode {
  MODE_AUTO = 0,
  MODE_MANUAL = 1
};

void systemModeInit();
void setSystemMode(SystemMode mode);
SystemMode getSystemMode();
bool isAutoMode();
bool isManualMode();

// Auto control cho từng thiết bị (có thể tắt riêng)
void setAutoFan(bool enable);
void setAutoPump(bool enable);
void setAutoLight(bool enable);

bool isAutoFanEnabled();
bool isAutoPumpEnabled();
bool isAutoLightEnabled();

#endif