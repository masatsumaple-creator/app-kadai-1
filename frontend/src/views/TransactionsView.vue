<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import {
  createTransaction,
  deleteTransaction,
  exportTransactions,
  fetchTransactions,
  importTransactions,
  updateTransaction,
} from "../api/transactions";
import { fetchCategories } from "../api/categories";

const transactions = ref([]);
const categories = ref([]);
const loading = ref(true);
const loadError = ref("");

const editingId = ref(null);
const formErrors = ref({});
const submitting = ref(false);

function emptyForm() {
  return { date: "", type: "expense", category_id: "", amount: "", memo: "" };
}

function emptyFilters() {
  return { from: "", to: "", category_id: "", type: "", keyword: "" };
}

const form = reactive(emptyForm());
const filters = reactive(emptyFilters());
const filterError = ref("");

const filteredCategories = computed(() =>
  categories.value.filter((c) => c.type === form.type)
);

const categoryNameById = computed(() => {
  const map = {};
  for (const c of categories.value) {
    map[c.id] = c.name;
  }
  return map;
});

function activeFilterParams() {
  const params = {};
  if (filters.from) params.from = filters.from;
  if (filters.to) params.to = filters.to;
  if (filters.category_id !== "") params.category_id = filters.category_id;
  if (filters.type) params.type = filters.type;
  if (filters.keyword) params.keyword = filters.keyword;
  return params;
}

async function loadAll() {
  loading.value = true;
  loadError.value = "";
  try {
    const [txs, cats] = await Promise.all([
      fetchTransactions(activeFilterParams()),
      fetchCategories(),
    ]);
    transactions.value = txs;
    categories.value = cats;
  } catch (e) {
    loadError.value = "データの取得に失敗しました。バックエンドが起動しているか確認してください。";
  } finally {
    loading.value = false;
  }
}

async function applyFilters() {
  filterError.value = "";
  try {
    transactions.value = await fetchTransactions(activeFilterParams());
  } catch (e) {
    filterError.value = e.response?.data?.errors
      ? Object.values(e.response.data.errors).join(" / ")
      : "絞り込みに失敗しました";
  }
}

function resetFilters() {
  Object.assign(filters, emptyFilters());
  filterError.value = "";
  applyFilters();
}

onMounted(loadAll);

function startEdit(tx) {
  editingId.value = tx.id;
  form.date = tx.date;
  form.type = tx.type;
  form.category_id = tx.category_id ?? "";
  form.amount = tx.amount;
  form.memo = tx.memo ?? "";
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
    date: form.date,
    type: form.type,
    category_id: form.category_id === "" ? null : Number(form.category_id),
    amount: form.amount === "" ? null : Number(form.amount),
    memo: form.memo || null,
  };

  try {
    if (editingId.value) {
      await updateTransaction(editingId.value, payload);
    } else {
      await createTransaction(payload);
    }
    cancelEdit();
    await applyFilters();
  } catch (e) {
    formErrors.value = e.response?.data?.errors || { form: "登録に失敗しました" };
  } finally {
    submitting.value = false;
  }
}

async function removeTransaction(id) {
  if (!confirm("この収支データを削除しますか？")) return;
  await deleteTransaction(id);
  await applyFilters();
}

async function handleExport() {
  const blob = await exportTransactions();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "transactions.csv";
  link.click();
  URL.revokeObjectURL(url);
}

const importResult = ref(null);
const importing = ref(false);
const fileInput = ref(null);

async function handleImport(event) {
  const file = event.target.files[0];
  if (!file) return;

  importing.value = true;
  importResult.value = null;
  try {
    importResult.value = await importTransactions(file);
    await applyFilters();
  } catch (e) {
    importResult.value = { imported: 0, failed: 0, errors: [], message: "インポートに失敗しました" };
  } finally {
    importing.value = false;
    if (fileInput.value) fileInput.value.value = "";
  }
}
</script>

<template>
  <section>
    <h1>収支一覧</h1>

    <form class="tx-form" @submit.prevent="submitForm">
      <h2>{{ editingId ? "収支データを編集" : "新規登録" }}</h2>

      <div class="field">
        <label>日付</label>
        <input v-model="form.date" type="date" required />
        <p v-if="formErrors.date" class="error">{{ formErrors.date }}</p>
      </div>

      <div class="field">
        <label>種別</label>
        <select v-model="form.type">
          <option value="expense">支出</option>
          <option value="income">収入</option>
        </select>
        <p v-if="formErrors.type" class="error">{{ formErrors.type }}</p>
      </div>

      <div class="field">
        <label>カテゴリ</label>
        <select v-model="form.category_id">
          <option value="">未分類</option>
          <option v-for="c in filteredCategories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
        <p v-if="formErrors.category_id" class="error">{{ formErrors.category_id }}</p>
      </div>

      <div class="field">
        <label>金額</label>
        <input v-model="form.amount" type="number" min="0" step="1" required />
        <p v-if="formErrors.amount" class="error">{{ formErrors.amount }}</p>
      </div>

      <div class="field">
        <label>メモ</label>
        <input v-model="form.memo" type="text" maxlength="255" />
      </div>

      <p v-if="formErrors.form" class="error">{{ formErrors.form }}</p>

      <div class="actions">
        <button type="submit" :disabled="submitting">
          {{ editingId ? "更新" : "登録" }}
        </button>
        <button v-if="editingId" type="button" @click="cancelEdit">キャンセル</button>
      </div>
    </form>

    <div class="csv-io">
      <h2>CSV入出力</h2>
      <div class="csv-actions">
        <button type="button" @click="handleExport">CSVエクスポート</button>
        <label class="file-input-label">
          CSVインポート
          <input
            ref="fileInput"
            type="file"
            accept=".csv,text/csv"
            :disabled="importing"
            @change="handleImport"
          />
        </label>
      </div>
      <div v-if="importResult" class="import-result">
        <p v-if="importResult.message" class="error">{{ importResult.message }}</p>
        <p v-else>
          {{ importResult.imported }}件インポートしました（失敗: {{ importResult.failed }}件）
        </p>
        <ul v-if="importResult.errors && importResult.errors.length > 0" class="import-errors">
          <li v-for="(err, i) in importResult.errors" :key="i">
            {{ err.line }}行目: {{ Object.values(err.errors).join(" / ") }}
          </li>
        </ul>
      </div>
    </div>

    <form class="filter-form" @submit.prevent="applyFilters">
      <h2>絞り込み</h2>

      <div class="field">
        <label>期間（から）</label>
        <input v-model="filters.from" type="date" />
      </div>

      <div class="field">
        <label>期間（まで）</label>
        <input v-model="filters.to" type="date" />
      </div>

      <div class="field">
        <label>種別</label>
        <select v-model="filters.type">
          <option value="">すべて</option>
          <option value="expense">支出</option>
          <option value="income">収入</option>
        </select>
      </div>

      <div class="field">
        <label>カテゴリ</label>
        <select v-model="filters.category_id">
          <option value="">すべて</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <div class="field">
        <label>キーワード（メモ）</label>
        <input v-model="filters.keyword" type="text" placeholder="例: スーパー" />
      </div>

      <div class="actions">
        <button type="submit">絞り込む</button>
        <button type="button" @click="resetFilters">リセット</button>
      </div>

      <p v-if="filterError" class="error">{{ filterError }}</p>
    </form>

    <p v-if="loading">読み込み中...</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <table v-else class="tx-table">
      <thead>
        <tr>
          <th>日付</th>
          <th>種別</th>
          <th>カテゴリ</th>
          <th>金額</th>
          <th>メモ</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="tx in transactions" :key="tx.id">
          <td>{{ tx.date }}</td>
          <td>{{ tx.type === "income" ? "収入" : "支出" }}</td>
          <td>{{ tx.category_id ? categoryNameById[tx.category_id] : "未分類" }}</td>
          <td>{{ tx.amount.toLocaleString() }}</td>
          <td>{{ tx.memo }}</td>
          <td class="row-actions">
            <button type="button" @click="startEdit(tx)">編集</button>
            <button type="button" @click="removeTransaction(tx.id)">削除</button>
          </td>
        </tr>
        <tr v-if="transactions.length === 0">
          <td colspan="6">データがありません</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.tx-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
}

.tx-form h2 {
  flex-basis: 100%;
  font-size: 1.1rem;
  margin: 0;
}

.csv-io {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
}

.csv-io h2 {
  font-size: 1rem;
  margin: 0 0 0.75rem;
}

.csv-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.import-result {
  margin-top: 0.75rem;
}

.import-errors {
  margin: 0.5rem 0 0;
  padding-left: 1.25rem;
  font-size: 0.85rem;
  color: #c0392b;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px dashed var(--border);
  border-radius: 6px;
}

.filter-form h2 {
  flex-basis: 100%;
  font-size: 1rem;
  margin: 0;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.error {
  color: #c0392b;
  font-size: 0.85rem;
  margin: 0;
}

.tx-table {
  width: 100%;
  border-collapse: collapse;
}

.tx-table th,
.tx-table td {
  border-bottom: 1px solid var(--border);
  padding: 0.5rem;
  text-align: left;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
}
</style>
