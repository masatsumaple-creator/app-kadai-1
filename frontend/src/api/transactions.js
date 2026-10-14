import { apiClient } from "./client";

export function fetchTransactions(params = {}) {
  return apiClient.get("/transactions", { params }).then((res) => res.data);
}

export function createTransaction(payload) {
  return apiClient.post("/transactions", payload).then((res) => res.data);
}

export function updateTransaction(id, payload) {
  return apiClient.put(`/transactions/${id}`, payload).then((res) => res.data);
}

export function deleteTransaction(id) {
  return apiClient.delete(`/transactions/${id}`);
}
