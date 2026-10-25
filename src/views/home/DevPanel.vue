<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import { initData, isTelegram } from '../../telegram'

const fallbackText = 'Init data не найдена. Откройте приложение из Telegram.'

const open = ref(false)
const copied = ref(false)
const textarea = useTemplateRef<{ $el: HTMLTextAreaElement }>('textarea')

function toggle() {
  open.value = !open.value
  copied.value = false
}

async function copyInitData() {
  try {
    await navigator.clipboard.writeText(initData)
    copied.value = true
  } catch {
    // Clipboard access can be blocked in some webviews; select the value for manual copying.
    textarea.value?.$el.select()
  }
}
</script>

<template>
  <section class="dev-panel" aria-label="Инструменты разработчика">
    <button type="button" class="dev-toggle" :aria-expanded="open" @click="toggle">
      <i class="pi pi-code dev-icon" aria-hidden="true" />
      <span class="dev-title">Для разработчиков</span>
      <Tag :severity="isTelegram ? 'success' : 'warn'" class="dev-status">
        <span class="status-dot" aria-hidden="true" />
        {{ isTelegram ? 'Telegram' : 'Браузер' }}
      </Tag>
      <i class="pi pi-chevron-down dev-chevron" :class="{ open }" aria-hidden="true" />
    </button>

    <div v-if="open" class="dev-body">
      <label class="dev-field">
        <span class="dev-label">Telegram init data</span>
        <Textarea
          ref="textarea"
          :model-value="initData || fallbackText"
          rows="5"
          readonly
          class="dev-init-data"
        />
      </label>
      <div class="dev-actions">
        <Button label="Скопировать" icon="pi pi-copy" :disabled="!initData" @click="copyInitData" />
        <span v-if="copied" role="status" class="dev-copied">
          <i class="pi pi-check" aria-hidden="true" />Скопировано
        </span>
      </div>
      <p class="dev-note">
        Видно только в тестовых окружениях. Панель ничего не отправляет на сервер.
      </p>
    </div>
  </section>
</template>

<style scoped>
.dev-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px dashed var(--p-surface-400);
  border-radius: var(--p-content-border-radius);
  background: var(--p-content-background);
}

.app-dark .dev-panel {
  border-color: var(--p-surface-600);
}

.dev-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  min-height: 3.5rem;
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: var(--p-text-color);
  text-align: left;
  cursor: pointer;
}

.dev-toggle:focus-visible {
  outline: 2px solid var(--p-primary-color);
  outline-offset: -2px;
}

.dev-icon {
  flex-shrink: 0;
  color: var(--p-surface-700);
  font-size: 1.125rem;
}

.app-dark .dev-icon {
  color: var(--p-surface-300);
}

.dev-title {
  flex: 1;
  min-width: 0;
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.25rem;
}

.dev-status {
  gap: 0.375rem;
}

.status-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  background: currentColor;
}

.dev-chevron {
  flex-shrink: 0;
  color: var(--p-surface-400);
  font-size: 0.875rem;
  transition: transform 0.15s;
}

.dev-chevron.open {
  transform: rotate(180deg);
}

.dev-body {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding: 0 1rem 1rem;
}

.dev-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.dev-label {
  color: var(--p-surface-700);
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1rem;
}

.app-dark .dev-label {
  color: var(--p-surface-300);
}

.dev-init-data {
  width: 100%;
  resize: none;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.75rem;
  line-height: 1.0625rem;
  word-break: break-all;
}

.dev-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

.dev-copied {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--p-primary-color);
  font-size: 0.8125rem;
  font-weight: 600;
}

.dev-copied .pi {
  font-size: 0.75rem;
}

.dev-note {
  margin: 0;
  color: var(--p-text-muted-color);
  font-size: 0.75rem;
  line-height: 1.0625rem;
}
</style>
