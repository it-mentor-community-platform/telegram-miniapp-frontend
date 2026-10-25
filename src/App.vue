<script setup lang="ts">
import { RouterView } from 'vue-router'
import ProgressSpinner from 'primevue/progressspinner'
import { session } from './session'
import AuthErrorView from './views/AuthErrorView.vue'
</script>

<template>
  <main class="app-shell">
    <!-- Auth screens replace the route without touching the URL, so the target page opens once
         authentication succeeds. -->
    <RouterView v-if="session.status === 'authenticated'" />
    <AuthErrorView
      v-else-if="session.status === 'outside-telegram' || session.status === 'failed'"
      :reason="session.status"
    />
    <div v-else class="app-loading">
      <ProgressSpinner stroke-width="4" aria-label="Вход" />
    </div>
  </main>
</template>

<style scoped>
/* Telegram sets the --tg-* safe area variables; they are absent in a regular browser. */
.app-shell {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 100vh;
  min-height: 100dvh;
  max-width: 30rem;
  margin: 0 auto;
  padding: calc(1.25rem + var(--tg-safe-area-inset-top, 0px) + var(--tg-content-safe-area-inset-top, 0px))
    calc(1rem + var(--tg-safe-area-inset-right, 0px))
    calc(1.5rem + var(--tg-safe-area-inset-bottom, 0px) + var(--tg-content-safe-area-inset-bottom, 0px))
    calc(1rem + var(--tg-safe-area-inset-left, 0px));
}

.app-loading {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
}
</style>
