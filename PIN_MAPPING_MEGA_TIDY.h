/*
 * PIN_MAPPING_MEGA_TIDY.h
 * Khai báo chân cho Arduino Mega - Smart Farm System
 * Tránh chân hỏng: D2, D5, D7, D8, D9
 * Author: LeHoangNhuan
 * Date: 2025-01-14
 */

#ifndef PIN_MAPPING_MEGA_TIDY_H
#define PIN_MAPPING_MEGA_TIDY_H

// ========== I2C (Mega) ==========
#define OLED_SDA_PIN 20
#define OLED_SCL_PIN 21
#define OLED_ADDRESS 0x3C

// ========== Servo ==========
#define SERVO_GATE_PIN 44       // Servo điều khiển CỔNG
#define SERVO_DOOR_PIN 45       // Servo điều khiển CỬA

// ========== Cảm biến Digital ==========
#define DHT_PIN 22              // DHT11 data
#define PIR_PIN 23              // PIR chuyển động
#define FLAME_PIN 24            // Cảm biến lửa
#define MQ2_DOUT_PIN 25         // MQ2 digital out (nếu dùng digital)
#define LDR_DOUT_PIN 26         // LDR digital out (nếu dùng digital)

// ========== Touch (4 nút) ==========
#define TOUCH_GATE_PIN 27       // Touch - Mở/đóng CỔNG
#define TOUCH_FAN_PIN 28        // Touch - Bật/Tắt QUẠT
#define TOUCH_DOOR_PIN 29       // Touch - Mở/đóng CỬA
#define TOUCH_PUMP_PIN 30       // Touch - Bật/Tắt BƠM

// ========== Buzzer ==========
#define BUZZER_PIN 31           // Buzzer

// ========== Relay ==========
#define RELAY_LIGHT 32          // Relay - ĐÈN
#define RELAY_FAN 33            // Relay - QUẠT
#define RELAY_PUMP 34           // Relay - BƠM

// ========== Analog (nếu dùng) ==========
#define MQ2_ANALOG_PIN A0       // MQ2 analog
#define LDR_ANALOG_PIN A1       // LDR analog

// ========== RC522 SPI (tùy chọn) ==========
#define RC522_MOSI_PIN 51
#define RC522_MISO_PIN 50
#define RC522_SCK_PIN 52
#define RC522_SS_PIN 53
#define RC522_RST_PIN 49

// ========== Ngưỡng cảm biến ==========
#define TEMP_HIGH 35
#define TEMP_NORMAL 33
#define HUMIDITY_LOW 50
#define GAS_THRESHOLD 300
#define LIGHT_THRESHOLD 500

// ========== Góc Servo ==========
#define SERVO_GATE_OPEN 60
#define SERVO_GATE_CLOSE 180
#define SERVO_DOOR_OPEN 60
#define SERVO_DOOR_CLOSE 180

// ========== Thời gian (ms) ==========
#define DEBOUNCE_DELAY 200
#define SENSOR_UPDATE 2000
#define OLED_UPDATE 3000
#define SERVO_DELAY 3000
#define BUZZER_DURATION 500
#define PUMP_DURATION 5000

#endif