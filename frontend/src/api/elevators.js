/**
 * Elevators API Module
 */

import { request } from "./client.js";

export async function fetchElevators() {
  return await request("/api/elevators/");
}

export async function fetchElevator(elevatorId) {
  return await request(`/api/elevators/${elevatorId}`);
}

export async function fetchElevatorHealth(elevatorId) {
  return await request(`/api/elevators/${elevatorId}/health`);
}
