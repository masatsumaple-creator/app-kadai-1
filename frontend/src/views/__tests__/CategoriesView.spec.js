import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CategoriesView from "../CategoriesView.vue";
import * as categoriesApi from "../../api/categories";

vi.mock("../../api/categories");

const sampleCategories = [
  { id: 1, name: "食費", type: "expense" },
  { id: 2, name: "給与", type: "income" },
];

beforeEach(() => {
  vi.resetAllMocks();
  categoriesApi.fetchCategories.mockResolvedValue(sampleCategories);
});

describe("CategoriesView", () => {
  it("splits categories into expense and income columns", async () => {
    const wrapper = mount(CategoriesView);
    await flushPromises();

    const columns = wrapper.findAll(".cat-column");
    expect(columns[0].text()).toContain("食費");
    expect(columns[0].text()).not.toContain("給与");
    expect(columns[1].text()).toContain("給与");
  });

  it("creates a category via the form", async () => {
    categoriesApi.createCategory.mockResolvedValue({ id: 3, name: "書籍代", type: "expense" });

    const wrapper = mount(CategoriesView);
    await flushPromises();

    await wrapper.find('input[type="text"]').setValue("書籍代");
    await wrapper.find("form.cat-form").trigger("submit");
    await flushPromises();

    expect(categoriesApi.createCategory).toHaveBeenCalledWith({ name: "書籍代", type: "expense" });
  });

  it("surfaces validation errors returned by the API", async () => {
    categoriesApi.createCategory.mockRejectedValue({
      response: { data: { errors: { name: "must be a non-empty string" } } },
    });

    const wrapper = mount(CategoriesView);
    await flushPromises();
    await wrapper.find("form.cat-form").trigger("submit");
    await flushPromises();

    expect(wrapper.text()).toContain("must be a non-empty string");
  });

  it("deletes a category after confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    categoriesApi.deleteCategory.mockResolvedValue();

    const wrapper = mount(CategoriesView);
    await flushPromises();

    await wrapper.findAll("button")
      .find((b) => b.text() === "削除")
      .trigger("click");
    await flushPromises();

    expect(categoriesApi.deleteCategory).toHaveBeenCalledWith(1);
  });
});
