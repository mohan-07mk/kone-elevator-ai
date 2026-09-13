/**
 * Base HTTP API Client
 */

const API_BASE_URL =
  (import.meta.env && (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || import.meta.env.REACT_APP_API_URL)) ||
  "https://kone-elevator-ai-production.up.railway.app";

export async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const token = localStorage.getItem("auth_token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(errorData.detail || `HTTP Error ${response.status}`);
      error.status = response.status;
      error.data = errorData;
      throw error;
    }
    if (response.status === 24) return null;
    return await response.json();
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const httpClient = {
  get: (endpoint, options) => request(endpoint, { ...options, method: "GET" }),
  post: (endpoint, body, options) => request(endpoint, { ...options, method: "POST", body: body ? JSON.stringify(body) : undefined }),
  put: (endpoint, body, options) => request(endpoint, { ...options, method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  delete: (endpoint, options) => request(endpoint, { ...options, method: "DELETE" }),
};

export { API_BASE_URL };
