import { createRouter, createWebHistory } from "vue-router";

import TransactionsView from "../views/TransactionsView.vue";
import CategoriesView from "../views/CategoriesView.vue";
import SummaryView from "../views/SummaryView.vue";
import BudgetsView from "../views/BudgetsView.vue";

const routes = [
  { path: "/", name: "transactions", component: TransactionsView },
  { path: "/categories", name: "categories", component: CategoriesView },
  { path: "/summary", name: "summary", component: SummaryView },
  { path: "/budgets", name: "budgets", component: BudgetsView },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
