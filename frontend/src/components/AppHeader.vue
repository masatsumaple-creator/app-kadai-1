<script setup></script>

<template>
  <header class="app-header">
    <h1 class="app-title">家計簿アプリ</h1>
    <nav class="app-nav">
      <RouterLink to="/">収支一覧</RouterLink>
      <RouterLink to="/categories">カテゴリ管理</RouterLink>
      <RouterLink to="/summary">集計・レポート</RouterLink>
      <RouterLink to="/budgets">予算設定</RouterLink>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #ddd;
}

.app-title {
  font-size: 1.25rem;
  margin: 0;
}

.app-nav {
  display: flex;
  gap: 1rem;
}

.app-nav a {
  text-decoration: none;
  color: inherit;
}

.app-nav a.router-link-active {
  font-weight: bold;
  text-decoration: underline;
}
</style>
