import { httpClient } from "./client.js";

export async function fetchRegisteredDevices() {
  return await httpClient.get("/api/devices");
}

export async function registerDevice(deviceData) {
  return await httpClient.post("/api/devices/register", deviceData);
}

export async function sendDeviceHeartbeat(heartbeatData) {
  return await httpClient.post("/api/devices/heartbeat", heartbeatData);
}

export async function ingestSTM32Telemetry(payload) {
  return await httpClient.post("/api/devices/stm32/ingest", payload);
}

export async function ingestRaspberryPiTelemetry(payload) {
  return await httpClient.post("/api/devices/raspberry-pi/ingest", payload);
}
