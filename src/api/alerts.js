import { httpClient } from "./client.js";

export async function fetchAlerts(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await httpClient.get(`/api/alerts${query ? `?${query}` : ""}`);
}

export async function acknowledgeAlert(alertId) {
  return await httpClient.post(`/api/alerts/${alertId}/acknowledge`);
}

export async function resolveAlert(alertId) {
  return await httpClient.post(`/api/alerts/${alertId}/resolve`);
}
