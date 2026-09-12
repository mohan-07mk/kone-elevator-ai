import { httpClient } from "./client.js";

export async function fetchPredictiveStatus(elevatorId) {
  return await httpClient.get(`/api/predictive/${elevatorId}`);
}

export async function triggerPredictiveAnalysis(elevatorId) {
  return await httpClient.post(`/api/predictive/analyze/${elevatorId}`);
}
