# Raspberry Pi Edge Gateway Client

## Overview
The Raspberry Pi Edge Gateway runs on edge Linux hardware deployed in building machine rooms. It interfaces with STM32 microcontroller nodes via USB/UART serial interfaces, buffers sensor telemetry locally in SQLite during network disconnects, and streams real-time HTTP POST requests to the FastAPI backend.

## Deployment Instructions
1. Install requirements:
   ```bash
   pip install requests
   ```
2. Run edge client:
   ```bash
   python edge_gateway.py
   ```
