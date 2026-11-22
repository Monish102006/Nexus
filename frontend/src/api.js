import axios from "axios";

const baseURL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

export const api = axios.create({ baseURL, timeout: 120000 });

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
