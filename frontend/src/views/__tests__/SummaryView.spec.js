import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import SummaryView from "../SummaryView.vue";
import * as summaryApi from "../../api/summary";
import * as categoriesApi from "../../api/categories";

vi.mock("../../api/summary");
vi.mock("../../api/categories");
vi.mock("vue-chartjs", () => ({
  Pie: { template: "<div class='pie-stub' />" },
  Bar: { template: "<div class='bar-stub' />" },
}));

const sampleSummary = {
  month: "2026-10",
  income_total: 300000,
  expense_total: 23000,
  balance: 277000,
  by_category: [
    { category_id: 1, name: "食費", type: "expense", total: 15000 },
    { category_id: 2, name: "交通費", type: "expense", total: 8000 },
    { category_id: 6, name: "給与", type: "income", total: 300000 },
  ],
};

const sampleTrend = [
  { month: "2026-09", income_total: 300000, expense_total: 20000, balance: 280000 },
  { month: "2026-10", income_total: 300000, expense_total: 23000, balance: 277000 },
];

const sampleCategories = [
  { id: 1, name: "食費", type: "expense" },
  { id: 2, name: "交通費", type: "expense" },
  { id: 6, name: "給与", type: "income" },
];

beforeEach(() => {
  vi.resetAllMocks();
  summaryApi.fetchMonthlySummary.mockResolvedValue(sampleSummary);
  summaryApi.fetchMonthlyTrend.mockResolvedValue(sampleTrend);
  categoriesApi.fetchCategories.mockResolvedValue(sampleCategories);
});

function mountView() {
  return mount(SummaryView, {
    global: { stubs: { VueDatePicker: true } },
  });
}

describe("SummaryView", () => {
  it("renders income/expense/balance totals", async () => {
    const wrapper = mountView();
    await flushPromises();

    expect(wrapper.text()).toContain("300,000");
    expect(wrapper.text()).toContain("23,000");
    expect(wrapper.text()).toContain("277,000");
  });

  it("lists expense-by-category rows in the data table, excluding income", async () => {
    const wrapper = mountView();
    await flushPromises();

    const table = wrapper.find(".data-table");
    expect(table.text()).toContain("食費");
    expect(table.text()).toContain("交通費");
    expect(table.text()).not.toContain("給与");
  });

  it("renders a trend row per month", async () => {
    const wrapper = mountView();
    await flushPromises();

    const tables = wrapper.findAll(".data-table");
    const trendTable = tables[1];
    expect(trendTable.text()).toContain("2026-09");
    expect(trendTable.text()).toContain("2026-10");
  });

  it("shows a load error message when the API call fails", async () => {
    summaryApi.fetchMonthlySummary.mockRejectedValue(new Error("network error"));
    const wrapper = mountView();
    await flushPromises();

    expect(wrapper.text()).toContain("バックエンドが起動しているか確認してください");
  });
});
