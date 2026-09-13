/**
 * Auth API Module
 */

import { request, API_BASE_URL } from "./client.js";

export async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const response = await fetch(`${API_BASE_URL}/api/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    throw new Error("Invalid credentials");
  }

  const data = await response.json();
  if (data.access_token) {
    localStorage.setItem("auth_token", data.access_token);
  }
  return data;
}

export async function getCurrentUser() {
  return await request("/api/auth/me");
}

export function logout() {
  localStorage.removeItem("auth_token");
}
