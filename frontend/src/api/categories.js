import { apiClient } from "./client";

export function fetchCategories() {
  return apiClient.get("/categories").then((res) => res.data);
}

export function createCategory(payload) {
  return apiClient.post("/categories", payload).then((res) => res.data);
}

export function updateCategory(id, payload) {
  return apiClient.put(`/categories/${id}`, payload).then((res) => res.data);
}

export function deleteCategory(id) {
  return apiClient.delete(`/categories/${id}`);
}
