import { apiClient } from "./client";

export function fetchMonthlySummary(month) {
  return apiClient.get("/summary", { params: { month } }).then((res) => res.data);
}

export function fetchMonthlyTrend() {
  return apiClient.get("/summary/trend").then((res) => res.data);
}
