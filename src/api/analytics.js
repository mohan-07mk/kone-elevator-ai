import { request } from "./client";

export async function fetchAnalyticsSummary(buildingId = "ALL") {
  return request(`/api/analytics/summary?building_id=${buildingId}`);
}

export async function fetchFaultDistribution(buildingId = "ALL") {
  return request(`/api/analytics/fault-distribution?building_id=${buildingId}`);
}

export async function fetchBuildingComparison() {
  return request("/api/analytics/building-comparison");
}

export async function fetchFaultTrends() {
  return request("/api/analytics/fault-trends");
}

export async function fetchMaintenanceTrends() {
  return request("/api/analytics/maintenance-trends");
}
