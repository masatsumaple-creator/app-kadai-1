import { apiClient } from "./client";

export function fetchCategories() {
  return apiClient.get("/categories").then((res) => res.data);
}
