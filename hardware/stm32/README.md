# STM32 Microcontroller Industrial Sensor Bridge

## Overview
This firmware module provides the high-frequency sensor acquisition and signal conditioning layer for physical elevator deployments.

## Specs & Protocol
- **Microcontroller Target**: STM32F407 / STM32H7 series (ARM Cortex-M4/M7)
- **Sampling Frequency**: 1 kHz ADC sampling rate for vibration & thermal sensors
- **Communications Interface**: USART1 (115200 8N1 baud)
- **Payload Format**: JSON Telemetry Frame matching the Elevator AI standard sensor contract:
  ```json
  {
    "device_id": "STM32-ELEV-001",
    "elevator_id": "KONE-ELEV-001",
    "motor_temp": 45.2,
    "voltage": 400.0,
    "current": 12.1,
    "power": 4840.0,
    "rpm": 1450.0,
    "vibration": 1.4,
    "brake": 95.0,
    "load": 40.0,
    "humidity": 50.0,
    "door": 0.0
  }
  ```
