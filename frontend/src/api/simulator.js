/**
 * Simulator Control API Module
 */

import { request } from "./client.js";

export async function fetchSimulatorStatus() {
  return await request("/api/simulator/status");
}

export async function startSimulator({ elevatorId = "KONE-ELEV-001", scenario = "BEARING_DEGRADATION", replaySpeed = 1.0 } = {}) {
  return await request("/api/simulator/start", {
    method: "POST",
    body: JSON.stringify({
      elevator_id: elevatorId,
      scenario,
      replay_speed: replaySpeed,
    }),
  });
}

export async function pauseSimulator() {
  return await request("/api/simulator/pause", {
    method: "POST",
  });
}

export async function resumeSimulator() {
  return await request("/api/simulator/resume", {
    method: "POST",
  });
}

export async function resetSimulator() {
  return await request("/api/simulator/reset", {
    method: "POST",
  });
}

export async function setSimulatorScenario({ scenario, elevatorId, replaySpeed } = {}) {
  return await request("/api/simulator/scenario", {
    method: "POST",
    body: JSON.stringify({
      scenario,
      elevator_id: elevatorId,
      replay_speed: replaySpeed,
    }),
  });
}
