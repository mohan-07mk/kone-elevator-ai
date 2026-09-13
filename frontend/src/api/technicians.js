import { request } from "./client";

export async function fetchTechnicians(availability = "All", specialization = "") {
  const query = new URLSearchParams();
  if (availability && availability !== "All") query.append("availability", availability);
  if (specialization) query.append("specialization", specialization);
  const qStr = query.toString() ? `?${query.toString()}` : "";
  return request(`/api/technicians${qStr}`);
}

export async function fetchTechnicianById(id) {
  return request(`/api/technicians/${id}`);
}

export async function recommendTechnician(elevatorId, faultType) {
  return request("/api/technicians/recommend", {
    method: "POST",
    body: JSON.stringify({ elevator_id: elevatorId, fault_type: faultType }),
  });
}
