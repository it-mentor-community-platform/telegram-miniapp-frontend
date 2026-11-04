<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import ProgressSpinner from 'primevue/progressspinner'
import AppShell from './components/AppShell.vue'
import { session } from './session'
import AuthErrorView from './views/AuthErrorView.vue'

// Test environments only (same flag as session's dummyAuthEnabled). Checked inline rather than via
// that export: Vite substitutes the value before bundling, so prod builds don't emit the chunk at all.
const DevLoginView =
  import.meta.env.VITE_SHOW_DEV_TOOLS === 'true'
    ? defineAsyncComponent(() => import('./views/DevLoginView.vue'))
    : undefined

const route = useRoute()
</script>

<template>
  <div class="app-safe-area flex min-h-dvh">
    <template v-if="session.status === 'authenticated'">
      <!-- Tablet and desktop only; the phone layout has Telegram's header instead. -->
      <AppShell v-if="route.meta.shell !== false" />
      <main class="flex min-w-0 flex-1 flex-col px-4 pt-5 pb-6 md:px-6 md:pt-6 md:pb-10 lg:px-10 lg:pt-8 lg:pb-12">
        <div class="mx-auto flex w-full max-w-120 flex-1 flex-col md:max-w-5xl">
          <RouterView />
        </div>
      </main>
    </template>

    <!-- Auth screens replace the route without touching the URL, so the target page opens once
         authentication succeeds. No shell; on wide layouts the screen sits in a centred card. -->
    <main v-else class="flex flex-1 flex-col px-4 pt-5 pb-6 md:items-center md:justify-center md:p-8">
      <div
        v-if="session.status !== 'pending'"
        class="mx-auto flex w-full max-w-120 flex-1 flex-col md:max-w-110 md:flex-none md:rounded-2xl md:border md:border-surface md:bg-(--p-content-background) md:p-8 md:shadow-raised"
      >
        <AuthErrorView
          v-if="
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
      </div>
      <div v-else class="flex flex-1 items-center justify-center">
        <ProgressSpinner stroke-width="4" aria-label="Вход" />
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Telegram sets the --tg-* safe area variables; they are absent in a regular browser. The layout's
   own padding is on <main> (Tailwind utilities per breakpoint). */
.app-safe-area {
  padding: calc(var(--tg-safe-area-inset-top, 0px) + var(--tg-content-safe-area-inset-top, 0px))
    var(--tg-safe-area-inset-right, 0px)
    calc(var(--tg-safe-area-inset-bottom, 0px) + var(--tg-content-safe-area-inset-bottom, 0px))
    var(--tg-safe-area-inset-left, 0px);
}
</style>
