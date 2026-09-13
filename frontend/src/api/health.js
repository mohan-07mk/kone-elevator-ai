import { httpClient } from "./client.js";

export async function fetchElevatorHealth(elevatorId) {
  return await httpClient.get(`/api/health/${elevatorId}`);
}

export async function updateHealthWeights(weights) {
  return await httpClient.post("/api/health/weights", weights);
}
