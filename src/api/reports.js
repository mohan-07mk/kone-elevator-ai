import { request } from "./client";

export async function generateReport(reportType, elevatorId = "ALL", buildingId = "ALL") {
  return request("/api/reports/generate", {
    method: "POST",
    body: JSON.stringify({
      report_type: reportType,
      elevator_id: elevatorId,
      building_id: buildingId,
    }),
  });
}

export async function fetchReportTemplates() {
  return request("/api/reports/list");
}
