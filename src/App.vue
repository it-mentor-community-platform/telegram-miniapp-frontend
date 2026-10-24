<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <main class="app-shell">
    <RouterView />
  </main>
</template>

<style scoped>
/* Telegram sets the --tg-* safe area variables; they are absent in a regular browser. */
.app-shell {
  width: 100%;
  max-width: 30rem;
  margin: 0 auto;
  padding: calc(1.25rem + var(--tg-safe-area-inset-top, 0px) + var(--tg-content-safe-area-inset-top, 0px))
    calc(1rem + var(--tg-safe-area-inset-right, 0px))
    calc(1.5rem + var(--tg-safe-area-inset-bottom, 0px) + var(--tg-content-safe-area-inset-bottom, 0px))
    calc(1rem + var(--tg-safe-area-inset-left, 0px));
}
</style>
