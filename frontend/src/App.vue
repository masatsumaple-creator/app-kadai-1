<script setup>
import AppHeader from "./components/AppHeader.vue";
</script>

<template>
  <AppHeader />
  <main class="app-main">
    <RouterView />
  </main>
</template>

<style scoped>
.app-main {
  max-width: 960px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
  box-sizing: border-box;
}

@media (max-width: 480px) {
  .app-main {
    padding: 1rem 0.75rem;
  }
}
</style>
