import { request } from "./client";

export async function fetchFaultTimeline(elevatorId = "ALL", limit = 20) {
  const query = new URLSearchParams();
  if (elevatorId && elevatorId !== "ALL") query.append("elevator_id", elevatorId);
  query.append("limit", limit);
  return request(`/api/timeline?${query.toString()}`);
}
