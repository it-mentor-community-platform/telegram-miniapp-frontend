<script setup lang="ts">
import { RouterView } from 'vue-router'
import ProgressSpinner from 'primevue/progressspinner'
import { session } from './session'
import AuthErrorView from './views/AuthErrorView.vue'
</script>

<template>
  <main class="app-shell mx-auto flex min-h-dvh w-full max-w-120 flex-col">
    <!-- Auth screens replace the route without touching the URL, so the target page opens once
         authentication succeeds. -->
    <RouterView v-if="session.status === 'authenticated'" />
    <AuthErrorView
      v-else-if="session.status === 'outside-telegram' || session.status === 'failed'"
      :reason="session.status"
    />
    <div v-else class="flex flex-1 items-center justify-center">
      <ProgressSpinner stroke-width="4" aria-label="Вход" />
    </div>
  </main>
</template>

<style scoped>
/* Telegram sets the --tg-* safe area variables; they are absent in a regular browser. */
.app-shell {
  padding: calc(1.25rem + var(--tg-safe-area-inset-top, 0px) + var(--tg-content-safe-area-inset-top, 0px))
    calc(1rem + var(--tg-safe-area-inset-right, 0px))
    calc(1.5rem + var(--tg-safe-area-inset-bottom, 0px) + var(--tg-content-safe-area-inset-bottom, 0px))
    calc(1rem + var(--tg-safe-area-inset-left, 0px));
}
</style>
