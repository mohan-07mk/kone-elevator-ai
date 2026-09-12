import { request } from "./client";

export async function fetchMaintenanceTasks(status = "All", elevatorId = "ALL", buildingId = "ALL") {
  const query = new URLSearchParams();
  if (status && status !== "All") query.append("status", status);
  if (elevatorId && elevatorId !== "ALL") query.append("elevator_id", elevatorId);
  if (buildingId && buildingId !== "ALL") query.append("building_id", buildingId);
  const qStr = query.toString() ? `?${query.toString()}` : "";
  return request(`/api/maintenance/tasks${qStr}`);
}

export async function createMaintenanceTask(payload) {
  return request("/api/maintenance/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function assignTechnicianToTask(taskId, technicianId) {
  return request(`/api/maintenance/tasks/${taskId}/assign`, {
    method: "POST",
    body: JSON.stringify({ technician_id: technicianId }),
  });
}

export async function completeMaintenanceTask(taskId) {
  return request(`/api/maintenance/tasks/${taskId}/complete`, {
    method: "POST",
  });
}

export async function fetchElevatorMaintenanceHistory(elevatorId) {
  return request(`/api/maintenance/history/${elevatorId}`);
}
