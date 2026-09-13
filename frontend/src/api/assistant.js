import { request } from "./client";

export async function askAIAssistant(message, elevatorId = "KONE-ELEV-001") {
  return request("/api/assistant/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      elevator_id: elevatorId,
    }),
  });
}
