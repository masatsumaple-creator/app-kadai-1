import { apiClient } from "./client";

export function fetchBudgets(month) {
  return apiClient.get("/budgets", { params: { month } }).then((res) => res.data);
}

export function createBudget(payload) {
  return apiClient.post("/budgets", payload).then((res) => res.data);
}

export function updateBudget(id, payload) {
  return apiClient.put(`/budgets/${id}`, payload).then((res) => res.data);
}

export function deleteBudget(id) {
  return apiClient.delete(`/budgets/${id}`);
}
