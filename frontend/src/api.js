import axios from "axios";

/**
 * Resolves and normalizes the backend API base URL.
 * Supports VITE_API_BASE_URL (and legacy VITE_API_URL).
 * Fallback for local development: http://127.0.0.1:8000
 * In production builds (if env not set): https://nexus-backend-d5th.onrender.com
 * Guarantees a single `/api` suffix without creating duplicate `/api/api`.
 */
export function resolveApiBaseUrl(customUrl) {
  const envUrl =
    customUrl ||
    import.meta.env.VITE_API_BASE_URL ||
    import.meta.env.VITE_API_URL;

  const defaultUrl = import.meta.env.PROD
    ? "https://nexus-backend-d5th.onrender.com"
    : "http://127.0.0.1:8000";

  const raw =
    (envUrl && typeof envUrl === "string" ? envUrl.trim() : "") || defaultUrl;
  const stripped = raw.replace(/\/+$/, "");
  return stripped.endsWith("/api") ? stripped : `${stripped}/api`;
}

export const API_BASE_URL = resolveApiBaseUrl();

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

// Guard against duplicate /api prefix if a caller accidentally includes /api in the path
api.interceptors.request.use((config) => {
  if (config.url) {
    if (config.url.startsWith("/api/")) {
      config.url = config.url.replace(/^\/api\//, "/");
    } else if (config.url === "/api") {
      config.url = "/";
    }
  }
  return config;
});

export const getHealth = () => api.get("/health").then((r) => r.data);
export const getMissions = () => api.get("/missions").then((r) => r.data);
export const getMission = (id) =>
  api.get(`/missions/${id}`).then((r) => r.data);
export const createMission = (objective) =>
  api.post("/missions", { objective }).then((r) => r.data);
export const getAgents = () => api.get("/agents").then((r) => r.data);
export const getApprovals = () => api.get("/approvals").then((r) => r.data);
export const approveAction = (id) =>
  api.post(`/approvals/${id}/approve`).then((r) => r.data);
export const rejectAction = (id) =>
  api.post(`/approvals/${id}/reject`).then((r) => r.data);
export const getActivity = (limit = 60) =>
  api.get(`/activity?limit=${limit}`).then((r) => r.data);

export function errText(error) {
  if (error?.response?.data?.detail) return error.response.data.detail;
  if (error?.response?.data) return JSON.stringify(error.response.data);
  if (error?.message) return error.message;
  return "Unexpected error";
}
