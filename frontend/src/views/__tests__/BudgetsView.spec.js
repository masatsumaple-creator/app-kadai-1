import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import BudgetsView from "../BudgetsView.vue";
import * as budgetsApi from "../../api/budgets";
import * as categoriesApi from "../../api/categories";

vi.mock("../../api/budgets");
vi.mock("../../api/categories");

const sampleCategories = [{ id: 1, name: "食費", type: "expense" }];

function mountView() {
  return mount(BudgetsView, {
    global: { stubs: { VueDatePicker: true } },
  });
}

beforeEach(() => {
  vi.resetAllMocks();
  categoriesApi.fetchCategories.mockResolvedValue(sampleCategories);
});

describe("BudgetsView", () => {
  it.each([
    [0.5, "順調"],
    [0.85, "もうすぐ上限"],
    [1.1, "予算超過"],
  ])("labels a budget at progress %s as %s", async (progress, label) => {
    budgetsApi.fetchBudgets.mockResolvedValue([
      { id: 1, category_id: 1, year_month: "2026-10", amount: 10000, spent: progress * 10000, remaining: 10000 - progress * 10000, progress },
    ]);

    const wrapper = mountView();
    await flushPromises();

    expect(wrapper.text()).toContain(label);
  });

  it("shows a message when there are no budgets for the month", async () => {
    budgetsApi.fetchBudgets.mockResolvedValue([]);
    const wrapper = mountView();
    await flushPromises();

    expect(wrapper.text()).toContain("この月の予算はまだ登録されていません");
  });

  it("deletes a budget after confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    budgetsApi.fetchBudgets.mockResolvedValue([
      { id: 1, category_id: 1, year_month: "2026-10", amount: 10000, spent: 1000, remaining: 9000, progress: 0.1 },
    ]);
    budgetsApi.deleteBudget.mockResolvedValue();

    const wrapper = mountView();
    await flushPromises();

    await wrapper.findAll("button")
      .find((b) => b.text() === "削除")
      .trigger("click");
    await flushPromises();

    expect(budgetsApi.deleteBudget).toHaveBeenCalledWith(1);
  });
});
