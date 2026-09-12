import { httpClient } from "./client.js";

export async function triggerAIDetection(elevatorId) {
  return await httpClient.post(`/api/ai/detect/${elevatorId}`);
}

export async function fetchRCA(elevatorId) {
  return await httpClient.get(`/api/ai/rca/${elevatorId}`);
}

export async function fetchMLEvaluation() {
  return await httpClient.get("/api/ai/evaluation");
}

export async function fetchAIStatus() {
  return await httpClient.get("/api/ai/status");
}

export async function runAIBenchmark(numPasses = 100) {
  return await httpClient.get(`/api/ai/benchmark?num_passes=${numPasses}`);
}
