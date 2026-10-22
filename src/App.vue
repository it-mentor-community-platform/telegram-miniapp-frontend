<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Textarea from 'primevue/textarea'

type Feedback = {
  severity: 'success' | 'error'
  text: string
}

const fallbackText = 'No Telegram init data found.'
const initData = ref('')
const isTelegram = ref(false)
const feedback = ref<Feedback | null>(null)

const displayData = computed(() => initData.value || fallbackText)
const hasInitData = computed(() => initData.value.length > 0)

onMounted(() => {
  const telegram = window.Telegram?.WebApp
  isTelegram.value = Boolean(telegram)

  if (telegram) {
    initData.value = telegram.initData || window.location.search.replace(/^\?/, '')
    document.documentElement.classList.toggle('app-dark', telegram.colorScheme === 'dark')
    telegram.ready()
    telegram.expand?.()
    return
  }

  initData.value = window.location.search.replace(/^\?/, '')
})

async function copyInitData() {
  if (!hasInitData.value) {
    feedback.value = {
      severity: 'error',
      text: 'There is no init data to copy.',
    }
    return
  }

  try {
    await navigator.clipboard.writeText(initData.value)
    feedback.value = {
      severity: 'success',
      text: 'Init data copied to the clipboard.',
    }
  } catch {
    feedback.value = {
      severity: 'error',
      text: 'Clipboard access failed. Select and copy the value manually.',
    }
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="hero" aria-labelledby="page-title">
      <div class="brand-mark" aria-hidden="true">
        <i class="pi pi-send" />
      </div>
      <div>
        <p class="eyebrow">IT Mentor Community</p>
        <h1 id="page-title">Telegram Mini App</h1>
        <p class="subtitle">
          The Vue and PrimeVue application is running. Use this development view to inspect
          Telegram launch data.
        </p>
      </div>
    </section>

    <Card class="data-card">
      <template #title>
        <div class="card-heading">
          <span>Telegram init data</span>
          <span class="connection-status" :class="{ connected: isTelegram }">
            <span class="status-dot" aria-hidden="true" />
            {{ isTelegram ? 'Telegram connected' : 'Browser preview' }}
          </span>
        </div>
      </template>

      <template #subtitle>
        This value is provided by Telegram when the Mini App opens. It remains in your browser
        and is not sent by this page.
      </template>

      <template #content>
        <Textarea
          :model-value="displayData"
          class="init-data"
          rows="9"
          readonly
          aria-label="Telegram init data"
        />

        <Message
          v-if="feedback"
          :severity="feedback.severity"
          :closable="true"
          class="feedback-message"
          @close="feedback = null"
        >
          {{ feedback.text }}
        </Message>
      </template>

      <template #footer>
        <div class="card-actions">
          <Button
            label="Copy init data"
            icon="pi pi-copy"
            :disabled="!hasInitData"
            @click="copyInitData"
          />
          <span v-if="!hasInitData" class="empty-hint">
            Open this page from Telegram or add query parameters for local testing.
          </span>
        </div>
      </template>
    </Card>
  </main>
</template>