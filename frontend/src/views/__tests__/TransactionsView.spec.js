import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TransactionsView from "../TransactionsView.vue";
import * as transactionsApi from "../../api/transactions";
import * as categoriesApi from "../../api/categories";

vi.mock("../../api/transactions");
vi.mock("../../api/categories");

const sampleTransactions = [
  { id: 1, category_id: 1, type: "expense", amount: 1500, date: "2026-10-02", memo: "スーパー" },
  { id: 2, category_id: null, type: "income", amount: 300000, date: "2026-10-01", memo: "給料" },
];

const sampleCategories = [
  { id: 1, name: "食費", type: "expense" },
  { id: 2, name: "給与", type: "income" },
];

function mountView() {
  return mount(TransactionsView, {
    global: { stubs: { VueDatePicker: true } },
  });
}

beforeEach(() => {
  vi.resetAllMocks();
  transactionsApi.fetchTransactions.mockResolvedValue(sampleTransactions);
  categoriesApi.fetchCategories.mockResolvedValue(sampleCategories);
});

describe("TransactionsView", () => {
  it("loads and renders transactions with resolved category names", async () => {
    const wrapper = mountView();
    await flushPromises();

    const rows = wrapper.findAll("tbody tr");
    expect(rows).toHaveLength(2);
    expect(wrapper.text()).toContain("食費");
    expect(wrapper.text()).toContain("未分類");
  });

  it("shows an empty-state row when there are no transactions", async () => {
    transactionsApi.fetchTransactions.mockResolvedValue([]);
    const wrapper = mountView();
    await flushPromises();

    expect(wrapper.text()).toContain("データがありません");
  });

  it("shows a load error message when the API call fails", async () => {
    transactionsApi.fetchTransactions.mockRejectedValue(new Error("network error"));
    const wrapper = mountView();
    await flushPromises();

    expect(wrapper.text()).toContain("バックエンドが起動しているか確認してください");
  });

  it("deletes a transaction after confirmation and reloads the list", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    transactionsApi.deleteTransaction.mockResolvedValue();

    const wrapper = mountView();
    await flushPromises();

    await wrapper.findAll("button")
      .find((b) => b.text() === "削除")
      .trigger("click");
    await flushPromises();

    expect(transactionsApi.deleteTransaction).toHaveBeenCalledWith(1);
  });

  it("does not delete when the user cancels the confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);

    const wrapper = mountView();
    await flushPromises();

    await wrapper.findAll("button")
      .find((b) => b.text() === "削除")
      .trigger("click");
    await flushPromises();

    expect(transactionsApi.deleteTransaction).not.toHaveBeenCalled();
  });

  it("submits the filter form with the entered keyword", async () => {
    transactionsApi.fetchTransactions.mockResolvedValue(sampleTransactions);
    const wrapper = mountView();
    await flushPromises();
    transactionsApi.fetchTransactions.mockClear();

    await wrapper.find('input[placeholder="例: スーパー"]').setValue("スーパー");
    await wrapper.find("form.filter-form").trigger("submit");
    await flushPromises();

    expect(transactionsApi.fetchTransactions).toHaveBeenCalledWith({ keyword: "スーパー" });
  });
});
