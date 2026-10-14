<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import {
  createBudget,
  deleteBudget,
  fetchBudgets,
  updateBudget,
} from "../api/budgets";
import { fetchCategories } from "../api/categories";
import { ja } from "date-fns/locale";

const STATUS_COLORS = {
  good: "#0ca30c",
  warning: "#fab219",
  critical: "#d03b3b",
};

function currentMonth() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

const month = ref(currentMonth());
const budgets = ref([]);
const categories = ref([]);
const loading = ref(true);
const loadError = ref("");

const editingId = ref(null);
const formErrors = ref({});
const submitting = ref(false);

function emptyForm() {
  return { category_id: "", amount: "" };
}

const form = reactive(emptyForm());

const expenseCategories = computed(() => categories.value.filter((c) => c.type === "expense"));

const categoryNameById = computed(() => {
  const map = {};
  for (const c of categories.value) map[c.id] = c.name;
  return map;
});

function statusFor(progress) {
  if (progress >= 1) return { key: "critical", label: "予算超過" };
  if (progress >= 0.8) return { key: "warning", label: "もうすぐ上限" };
  return { key: "good", label: "順調" };
}

async function loadAll() {
  loading.value = true;
  loadError.value = "";
  try {
    const [budgetList, categoryList] = await Promise.all([
      fetchBudgets(month.value),
      fetchCategories(),
    ]);
    budgets.value = budgetList;
    categories.value = categoryList;
  } catch (e) {
    loadError.value = "予算データの取得に失敗しました。バックエンドが起動しているか確認してください。";
  } finally {
    loading.value = false;
  }
}

onMounted(loadAll);
watch(month, loadAll);

function startEdit(budget) {
  editingId.value = budget.id;
  form.category_id = budget.category_id;
  form.amount = budget.amount;
  formErrors.value = {};
}

function cancelEdit() {
  editingId.value = null;
  Object.assign(form, emptyForm());
  formErrors.value = {};
}

async function submitForm() {
  formErrors.value = {};
  submitting.value = true;

  const payload = {
    category_id: form.category_id === "" ? null : Number(form.category_id),
    year_month: month.value,
    amount: form.amount === "" ? null : Number(form.amount),
  };

  try {
    if (editingId.value) {
      await updateBudget(editingId.value, payload);
    } else {
      await createBudget(payload);
    }
    cancelEdit();
    await loadAll();
  } catch (e) {
    formErrors.value = e.response?.data?.errors || { form: "登録に失敗しました" };
  } finally {
    submitting.value = false;
  }
}

async function removeBudget(id) {
  if (!confirm("この予算を削除しますか？")) return;
  await deleteBudget(id);
  await loadAll();
}
</script>

<template>
  <section>
    <h1>予算設定</h1>

    <div class="field month-field">
      <label>対象月</label>
      <VueDatePicker
        v-model="month"
        month-picker
        model-type="yyyy-MM"
        format="yyyy-MM"
        :locale="ja"
        :clearable="false"
        auto-apply
      />
    </div>

    <form class="budget-form" @submit.prevent="submitForm">
      <h2>{{ editingId ? "予算を編集" : "新規登録" }}</h2>

      <div class="field">
        <label>カテゴリ</label>
        <select v-model="form.category_id" :disabled="!!editingId">
          <option value="">選択してください</option>
          <option v-for="c in expenseCategories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
        <p v-if="formErrors.category_id" class="error">{{ formErrors.category_id }}</p>
      </div>

      <div class="field">
        <label>予算額</label>
        <input v-model="form.amount" type="number" min="0" step="1" required />
        <p v-if="formErrors.amount" class="error">{{ formErrors.amount }}</p>
      </div>

      <p v-if="formErrors.budget" class="error">{{ formErrors.budget }}</p>
      <p v-if="formErrors.form" class="error">{{ formErrors.form }}</p>

      <div class="actions">
        <button type="submit" :disabled="submitting">
          {{ editingId ? "更新" : "登録" }}
        </button>
        <button v-if="editingId" type="button" @click="cancelEdit">キャンセル</button>
      </div>
    </form>

    <p v-if="loading">読み込み中...</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <ul v-else class="budget-list">
      <li v-for="b in budgets" :key="b.id" class="budget-item">
        <div class="budget-header">
          <span class="budget-name">{{ categoryNameById[b.category_id] }}</span>
          <span class="budget-status" :style="{ color: STATUS_COLORS[statusFor(b.progress).key] }">
            {{ statusFor(b.progress).label }}
          </span>
        </div>
        <div class="progress-track">
          <div
            class="progress-fill"
            :style="{
              width: Math.min(b.progress * 100, 100) + '%',
              backgroundColor: STATUS_COLORS[statusFor(b.progress).key],
            }"
          />
        </div>
        <div class="budget-figures">
          <span>使用: {{ b.spent.toLocaleString() }} / {{ b.amount.toLocaleString() }}</span>
          <span>残り: {{ b.remaining.toLocaleString() }}</span>
        </div>
        <div class="row-actions">
          <button type="button" @click="startEdit(b)">編集</button>
          <button type="button" @click="removeBudget(b.id)">削除</button>
        </div>
      </li>
      <li v-if="budgets.length === 0">この月の予算はまだ登録されていません</li>
    </ul>
  </section>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.month-field {
  max-width: 200px;
  margin-bottom: 1.5rem;
}

.budget-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
}

.budget-form h2 {
  flex-basis: 100%;
  font-size: 1.1rem;
  margin: 0;
}

.error {
  color: #c0392b;
  font-size: 0.85rem;
  margin: 0;
}

.budget-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.budget-item {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
}

.budget-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.budget-name {
  font-weight: 600;
}

.budget-status {
  font-weight: 600;
  font-size: 0.9rem;
}

.progress-track {
  height: 10px;
  border-radius: 5px;
  background: var(--border);
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.2s ease;
}

.budget-figures {
  display: flex;
  justify-content: space-between;
  font-variant-numeric: tabular-nums;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
}
</style>
