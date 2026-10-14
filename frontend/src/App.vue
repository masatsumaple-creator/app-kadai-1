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
  padding: 1.5rem;
}
</style>
