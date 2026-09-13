/**
 * Sensors & Telemetry API Module
 */

import { request } from "./client.js";

export async function fetchLatestSensors(elevatorId) {
  return await request(`/api/elevators/${elevatorId}/sensors/latest`);
}

export async function fetchSensorHistory(elevatorId, limit = 100, offset = 0) {
  return await request(`/api/elevators/${elevatorId}/sensors/history?limit=${limit}&offset=${offset}`);
}

export async function fetchSingleSensorHistory(elevatorId, sensorKey, limit = 100, offset = 0) {
  return await request(`/api/elevators/${elevatorId}/sensors/${sensorKey}/history?limit=${limit}&offset=${offset}`);
}

export async function ingestTelemetry(telemetryData) {
  return await request("/api/sensors/ingest", {
    method: "POST",
    body: JSON.stringify(telemetryData),
  });
}
