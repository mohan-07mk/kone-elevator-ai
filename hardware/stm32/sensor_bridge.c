/**
 * STM32 Microcontroller Industrial Sensor Bridge Code
 *
 * Samples tri-axial vibration (accelerometer), motor temperature (thermocouple),
 * and motor current (hall effect sensor) at 1 kHz, normalizes raw ADC values,
 * and serializes telemetry payload over UART JSON protocol to Raspberry Pi Edge Gateway.
 */

#include <stdio.h>
#include <string.h>
#include <math.h>

// Simulated HAL types for build demonstration
typedef unsigned int uint32_t;
typedef unsigned short uint16_t;

typedef struct {
    float motor_temp;
    float voltage;
    float current;
    float power;
    float rpm;
    float vibration;
    float brake;
    float load;
    float humidity;
    float door;
} SensorFrame;

// Convert raw 12-bit ADC reading to vibration magnitude (mm/s)
float read_vibration_sensor(uint16_t adc_val) {
    float voltage = (adc_val / 4095.0f) * 3.3f;
    return (voltage - 1.65f) * 12.5f; // Scale factor: 12.5 mm/s per Volt
}

// Convert raw 12-bit ADC reading to motor temperature (°C)
float read_temp_sensor(uint16_t adc_val) {
    float voltage = (adc_val / 4095.0f) * 3.3f;
    return (voltage * 100.0f); // LM35 scale: 10mV/°C
}

// Serialize telemetry frame to JSON string over UART
int serialize_telemetry_frame(const SensorFrame* frame, char* buffer, size_t max_len) {
    return snprintf(buffer, max_len,
        "{\"device_id\":\"STM32-ELEV-001\",\"elevator_id\":\"KONE-ELEV-001\","
        "\"motor_temp\":%.2f,\"voltage\":%.2f,\"current\":%.2f,\"power\":%.2f,"
        "\"rpm\":%.2f,\"vibration\":%.2f,\"brake\":%.2f,\"load\":%.2f,"
        "\"humidity\":%.2f,\"door\":%.2f}\r\n",
        frame->motor_temp, frame->voltage, frame->current, frame->power,
        frame->rpm, frame->vibration, frame->brake, frame->load,
        frame->humidity, frame->door
    );
}

int main(void) {
    SensorFrame sample = {
        .motor_temp = 45.2f,
        .voltage = 400.0f,
        .current = 12.1f,
        .power = 4840.0f,
        .rpm = 1450.0f,
        .vibration = 1.4f,
        .brake = 95.0f,
        .load = 40.0f,
        .humidity = 50.0f,
        .door = 0.0f
    };

    char json_buf[256];
    serialize_telemetry_frame(&sample, json_buf, sizeof(json_buf));
    printf("STM32 UART Packet: %s", json_buf);
    return 0;
}
