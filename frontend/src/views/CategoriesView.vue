<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import {
  createCategory,
  deleteCategory,
  fetchCategories,
  updateCategory,
} from "../api/categories";

const categories = ref([]);
const loading = ref(true);
const loadError = ref("");

const editingId = ref(null);
const formErrors = ref({});
const submitting = ref(false);

function emptyForm() {
  return { name: "", type: "expense" };
}

const form = reactive(emptyForm());

const expenseCategories = computed(() => categories.value.filter((c) => c.type === "expense"));
const incomeCategories = computed(() => categories.value.filter((c) => c.type === "income"));

async function loadCategories() {
  loading.value = true;
  loadError.value = "";
  try {
    categories.value = await fetchCategories();
  } catch (e) {
    loadError.value = "カテゴリの取得に失敗しました。バックエンドが起動しているか確認してください。";
  } finally {
    loading.value = false;
  }
}

onMounted(loadCategories);

function startEdit(category) {
  editingId.value = category.id;
  form.name = category.name;
  form.type = category.type;
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

  const payload = { name: form.name, type: form.type };

  try {
    if (editingId.value) {
      await updateCategory(editingId.value, payload);
    } else {
      await createCategory(payload);
    }
    cancelEdit();
    await loadCategories();
  } catch (e) {
    formErrors.value = e.response?.data?.errors || { form: "登録に失敗しました" };
  } finally {
    submitting.value = false;
  }
}

async function removeCategory(category) {
  const message =
    `「${category.name}」を削除しますか？\n` +
    "紐づく収支データは未分類になり、紐づく予算は削除されます。";
  if (!confirm(message)) return;
  await deleteCategory(category.id);
  await loadCategories();
}
</script>

<template>
  <section>
    <h1>カテゴリ管理</h1>

    <form class="cat-form" @submit.prevent="submitForm">
      <h2>{{ editingId ? "カテゴリを編集" : "新規登録" }}</h2>

      <div class="field">
        <label>名前</label>
        <input v-model="form.name" type="text" maxlength="100" required />
        <p v-if="formErrors.name" class="error">{{ formErrors.name }}</p>
      </div>

      <div class="field">
        <label>種別</label>
        <select v-model="form.type">
          <option value="expense">支出</option>
          <option value="income">収入</option>
        </select>
        <p v-if="formErrors.type" class="error">{{ formErrors.type }}</p>
      </div>

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

    <div v-else class="cat-columns">
      <div class="cat-column">
        <h2>支出カテゴリ</h2>
        <ul class="cat-list">
          <li v-for="c in expenseCategories" :key="c.id">
            <span>{{ c.name }}</span>
            <span class="row-actions">
              <button type="button" @click="startEdit(c)">編集</button>
              <button type="button" @click="removeCategory(c)">削除</button>
            </span>
          </li>
          <li v-if="expenseCategories.length === 0">カテゴリがありません</li>
        </ul>
      </div>

      <div class="cat-column">
        <h2>収入カテゴリ</h2>
        <ul class="cat-list">
          <li v-for="c in incomeCategories" :key="c.id">
            <span>{{ c.name }}</span>
            <span class="row-actions">
              <button type="button" @click="startEdit(c)">編集</button>
              <button type="button" @click="removeCategory(c)">削除</button>
            </span>
          </li>
          <li v-if="incomeCategories.length === 0">カテゴリがありません</li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cat-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
}

.cat-form h2 {
  flex-basis: 100%;
  font-size: 1.1rem;
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

.cat-columns {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.cat-column {
  flex: 1 1 280px;
}

.cat-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.cat-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
}

.row-actions {
  display: flex;
  gap: 0.5rem;
}
</style>
