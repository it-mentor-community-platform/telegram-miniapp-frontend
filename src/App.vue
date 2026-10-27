<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import { RouterView } from 'vue-router'
import ProgressSpinner from 'primevue/progressspinner'
import { session } from './session'
import AuthErrorView from './views/AuthErrorView.vue'

// Test environments only (same flag as session's dummyAuthEnabled). Checked inline rather than via
// that export: Vite substitutes the value before bundling, so prod builds don't emit the chunk at all.
const DevLoginView =
  import.meta.env.VITE_SHOW_DEV_TOOLS === 'true'
    ? defineAsyncComponent(() => import('./views/DevLoginView.vue'))
    : undefined
</script>

<template>
  <main class="app-shell mx-auto flex min-h-dvh w-full max-w-120 flex-col">
    <!-- Auth screens replace the route without touching the URL, so the target page opens once
         authentication succeeds. -->
    <RouterView v-if="session.status === 'authenticated'" />
    <AuthErrorView
      v-else-if="
        session.status === 'outside-telegram' ||
        session.status === 'failed' ||
        session.status === 'expired'
      "
      :reason="session.status"
    />
    <DevLoginView
      v-else-if="
        DevLoginView && (session.status === 'dummy-login' || session.status === 'dummy-expired')
      "
      :expired="session.status === 'dummy-expired'"
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
