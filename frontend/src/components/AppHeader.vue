<script setup></script>

<template>
  <header class="app-header">
    <h1 class="app-title">💰 家計簿アプリ</h1>
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
  background: linear-gradient(90deg, var(--accent), var(--teal));
  color: #ffffff;
}

.app-title {
  font-size: 1.25rem;
  margin: 0;
  white-space: nowrap;
}

.app-nav {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.app-nav a {
  text-decoration: none;
  color: #ffffff;
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  opacity: 0.85;
}

.app-nav a:hover {
  background: rgba(255, 255, 255, 0.15);
  opacity: 1;
}

.app-nav a.router-link-active {
  background: rgba(255, 255, 255, 0.25);
  font-weight: 600;
  opacity: 1;
}
</style>
