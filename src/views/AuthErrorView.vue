<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import { authenticate } from '../session'

// Shown by the app shell instead of any route; see design/AuthError.dc.html.
const props = defineProps<{
  reason: 'outside-telegram' | 'failed'
}>()

const telegramAppUrl = `https://t.me/${import.meta.env.VITE_TELEGRAM_BOT_USERNAME}?startapp`

const steps = [
  'Нажмите «Открыть в Telegram» — приложение откроется на той же странице.',
  'Или найдите бота сообщества в Telegram и нажмите кнопку приложения.',
  'Вход произойдёт сам — логин и пароль не нужны.',
]

const retrying = ref(false)

async function retry() {
  retrying.value = true
  try {
    await authenticate()
  } finally {
    retrying.value = false
  }
}

const failed = props.reason === 'failed'
</script>

<template>
  <div class="auth-error">
    <div class="auth-main">
      <span class="auth-icon" :class="{ failed }" aria-hidden="true">
        <i :class="['pi', failed ? 'pi-shield' : 'pi-telegram']" />
      </span>

      <div class="auth-copy">
        <template v-if="failed">
          <h1 class="auth-title">Не удалось войти</h1>
          <p class="auth-text">
            Telegram не подтвердил вход или сервер сейчас недоступен. Попробуйте ещё раз — если
            ошибка повторится, напишите нам.
          </p>
        </template>
        <template v-else>
          <h1 class="auth-title">Откройте приложение в Telegram</h1>
          <p class="auth-text">
            IT Ментор — мини-приложение Telegram. Вход происходит автоматически через ваш аккаунт,
            поэтому в обычном браузере приложение не работает.
          </p>
        </template>
      </div>

      <ol v-if="!failed" class="auth-steps">
        <li v-for="(step, index) in steps" :key="step" class="auth-step">
          <span class="auth-step-number" aria-hidden="true">{{ index + 1 }}</span>
          <span class="auth-step-text">{{ step }}</span>
        </li>
      </ol>
    </div>

    <div class="auth-actions">
      <template v-if="failed">
        <Button
          label="Попробовать снова"
          icon="pi pi-refresh"
          :loading="retrying"
          size="large"
          @click="retry"
        />
        <Button
          as="a"
          href="https://t.me/zhukovsd_it_chat"
          target="_blank"
          rel="noopener"
          label="Написать в чат сообщества"
          text
        />
      </template>
      <template v-else>
        <Button
          as="a"
          :href="telegramAppUrl"
          label="Открыть в Telegram"
          icon="pi pi-external-link"
          size="large"
        />
        <Button
          as="a"
          href="https://telegram.org/apps"
          target="_blank"
          rel="noopener"
          label="Нет Telegram? Установить"
          text
        />
      </template>
    </div>
  </div>
</template>

<style scoped>
/* Fills the app shell, whose padding already includes the safe areas. */
.auth-error {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 1.5rem;
}

.auth-main {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  text-align: center;
}

.auth-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 50%;
  background: var(--p-emerald-50);
  color: var(--p-emerald-700);
}

.auth-icon .pi {
  font-size: 2rem;
}

.auth-icon.failed {
  background: var(--p-orange-50);
  color: var(--p-orange-700);
}

.app-dark .auth-icon {
  background: color-mix(in srgb, var(--p-emerald-400) 16%, transparent);
  color: var(--p-emerald-300);
}

.app-dark .auth-icon.failed {
  background: color-mix(in srgb, var(--p-orange-500) 16%, transparent);
  color: var(--p-orange-300);
}

.auth-copy {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 20rem;
}

.auth-title {
  margin: 0;
  font-size: 1.375rem;
  font-weight: 700;
  line-height: 1.75rem;
}

.auth-text {
  margin: 0;
  color: var(--p-text-muted-color);
  font-size: 0.9375rem;
  line-height: 1.375rem;
}

.auth-steps {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
  margin: 0;
  padding: 1rem;
  list-style: none;
  border: 1px solid var(--p-content-border-color);
  border-radius: var(--p-content-border-radius);
  background: var(--p-content-background);
  text-align: left;
}

.auth-step {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  color: var(--p-surface-700);
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.app-dark .auth-step {
  color: var(--p-surface-300);
}

.auth-step-number {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: var(--p-surface-100);
  color: var(--p-text-color);
  font-size: 0.75rem;
  font-weight: 700;
}

.app-dark .auth-step-number {
  background: var(--p-surface-800);
}

.auth-step-text {
  padding-top: 0.125rem;
}

.auth-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Link buttons (as="a") would otherwise get the browser's link underline. */
.auth-actions a {
  text-decoration: none;
}
</style>
