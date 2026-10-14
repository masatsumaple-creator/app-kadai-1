<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { Bar, Pie } from "vue-chartjs";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
  ArcElement,
} from "chart.js";
import { fetchMonthlySummary, fetchMonthlyTrend } from "../api/summary";
import { fetchCategories } from "../api/categories";

ChartJS.register(BarElement, CategoryScale, LinearScale, Legend, Tooltip, ArcElement);

// Fixed categorical order (validated palette, see dataviz skill references/palette.md).
const CATEGORY_COLORS = [
  "#2a78d6", // blue
  "#eb6834", // orange
  "#1baf7a", // aqua
  "#eda100", // yellow
  "#e87ba4", // magenta
  "#008300", // green
  "#4a3aa7", // violet
  "#e34948", // red
];
const INCOME_COLOR = CATEGORY_COLORS[0];
const EXPENSE_COLOR = CATEGORY_COLORS[1];

function currentMonth() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

const month = ref(currentMonth());
const summary = ref(null);
const trend = ref([]);
const categoryColorById = ref({});
const loading = ref(true);
const loadError = ref("");

const expenseByCategory = computed(
  () => summary.value?.by_category.filter((c) => c.type === "expense") || []
);

const pieChartData = computed(() => ({
  labels: expenseByCategory.value.map((c) => c.name),
  datasets: [
    {
      data: expenseByCategory.value.map((c) => c.total),
      backgroundColor: expenseByCategory.value.map(
        (c) => categoryColorById.value[c.category_id] || "#898781"
      ),
    },
  ],
}));

const pieChartOptions = {
  responsive: true,
  plugins: { legend: { position: "bottom" } },
};

const trendChartData = computed(() => ({
  labels: trend.value.map((t) => t.month),
  datasets: [
    { label: "収入", data: trend.value.map((t) => t.income_total), backgroundColor: INCOME_COLOR },
    { label: "支出", data: trend.value.map((t) => t.expense_total), backgroundColor: EXPENSE_COLOR },
  ],
}));

const trendChartOptions = {
  responsive: true,
  scales: { y: { beginAtZero: true } },
  plugins: { legend: { position: "bottom" } },
};

async function loadCategoryColors() {
  const categories = await fetchCategories();
  const expenseCategories = categories
    .filter((c) => c.type === "expense")
    .sort((a, b) => a.id - b.id);
  const map = {};
  expenseCategories.forEach((c, i) => {
    map[c.id] = CATEGORY_COLORS[i % CATEGORY_COLORS.length];
  });
  categoryColorById.value = map;
}

async function loadSummary() {
  loading.value = true;
  loadError.value = "";
  try {
    const [monthlySummary, monthlyTrend] = await Promise.all([
      fetchMonthlySummary(month.value),
      fetchMonthlyTrend(),
    ]);
    summary.value = monthlySummary;
    trend.value = monthlyTrend;
  } catch (e) {
    loadError.value = "集計データの取得に失敗しました。バックエンドが起動しているか確認してください。";
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadCategoryColors();
  await loadSummary();
});
watch(month, loadSummary);
</script>

<template>
  <section>
    <h1>集計・レポート</h1>

    <div class="field month-field">
      <label>対象月</label>
      <input v-model="month" type="month" />
    </div>

    <p v-if="loading">読み込み中...</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <template v-else>
      <div class="totals">
        <div class="stat-tile">
          <span class="stat-label">収入</span>
          <span class="stat-value">{{ summary.income_total.toLocaleString() }}</span>
        </div>
        <div class="stat-tile">
          <span class="stat-label">支出</span>
          <span class="stat-value">{{ summary.expense_total.toLocaleString() }}</span>
        </div>
        <div class="stat-tile">
          <span class="stat-label">差額</span>
          <span class="stat-value">{{ summary.balance.toLocaleString() }}</span>
        </div>
      </div>

      <h2>カテゴリ別支出（{{ month }}）</h2>
      <div v-if="expenseByCategory.length === 0">この月の支出データがありません</div>
      <div v-else class="chart-with-table">
        <div class="chart-box">
          <Pie :data="pieChartData" :options="pieChartOptions" />
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>カテゴリ</th>
              <th>金額</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in expenseByCategory" :key="c.category_id">
              <td>{{ c.name }}</td>
              <td>{{ c.total.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2>月別収支推移</h2>
      <div v-if="trend.length === 0">データがありません</div>
      <div v-else class="chart-with-table">
        <div class="chart-box">
          <Bar :data="trendChartData" :options="trendChartOptions" />
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>月</th>
              <th>収入</th>
              <th>支出</th>
              <th>差額</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in trend" :key="t.month">
              <td>{{ t.month }}</td>
              <td>{{ t.income_total.toLocaleString() }}</td>
              <td>{{ t.expense_total.toLocaleString() }}</td>
              <td>{{ t.balance.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </section>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 1.5rem;
}

.month-field {
  max-width: 200px;
}

.error {
  color: #c0392b;
}

.totals {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-tile {
  flex: 1;
  padding: 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text);
  opacity: 0.7;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.chart-with-table {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
  align-items: flex-start;
}

.chart-box {
  flex: 1 1 320px;
  max-width: 420px;
}

.data-table {
  flex: 1 1 280px;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  border-bottom: 1px solid var(--border);
  padding: 0.4rem 0.75rem;
  text-align: left;
  font-variant-numeric: tabular-nums;
}
</style>
