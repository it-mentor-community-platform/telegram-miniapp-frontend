<script setup lang="ts">
import { ref } from 'vue'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Card from 'primevue/card'
import { authenticate } from '../session'
import { closeApp } from '../telegram'

// Shown by the app shell instead of any route; see design/AuthError.dc.html.
const props = defineProps<{
  reason: 'outside-telegram' | 'failed' | 'expired'
}>()

const content = {
  'outside-telegram': {
    icon: 'pi pi-telegram',
    tint: 'tint-success',
    title: 'Откройте приложение в Telegram',
    text: 'IT Ментор — мини-приложение Telegram. Вход происходит автоматически через ваш аккаунт, поэтому в обычном браузере приложение не работает.',
  },
  failed: {
    icon: 'pi pi-shield',
    tint: 'tint-warn',
    title: 'Не удалось войти',
    text: 'Telegram не подтвердил вход или сервер сейчас недоступен. Попробуйте ещё раз — если ошибка повторится, напишите нам.',
  },
  expired: {
    icon: 'pi pi-clock',
    tint: 'tint-warn',
    title: 'Сессия истекла',
    text: 'Прошло больше 30 минут с момента входа. Закройте приложение и откройте его снова — вход произойдёт автоматически.',
  },
}[props.reason]

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

const outside = props.reason === 'outside-telegram'
</script>

<template>
  <!-- Fills the app shell, whose padding already includes the safe areas. -->
  <div class="flex flex-1 flex-col gap-6">
    <div class="flex flex-1 flex-col items-center justify-center gap-5 text-center">
      <Avatar
        :icon="content.icon"
        shape="circle"
        class="size-18"
        :class="content.tint"
        pt:icon:class="text-[2rem]"
        aria-hidden="true"
      />

      <div class="flex max-w-80 flex-col gap-2">
        <h1 class="text-page font-bold">{{ content.title }}</h1>
        <p class="text-md/[1.375rem] text-muted-color">{{ content.text }}</p>
      </div>

      <Card v-if="outside" class="w-full text-left">
        <template #content>
          <ol class="flex flex-col gap-3">
            <li
              v-for="(step, index) in steps"
              :key="step"
              class="flex items-start gap-3 text-sm text-(--p-tint-neutral-color)"
            >
              <Avatar
                :label="String(index + 1)"
                shape="circle"
                class="size-6 shrink-0 text-xs font-bold text-color"
                aria-hidden="true"
              />
              <span class="pt-0.5">{{ step }}</span>
            </li>
          </ol>
        </template>
      </Card>
    </div>

    <div class="flex flex-col gap-2">
      <template v-if="outside">
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
      <template v-else>
        <Button
          v-if="reason === 'failed'"
          label="Попробовать снова"
          icon="pi pi-refresh"
          :loading="retrying"
          size="large"
          @click="retry"
        />
        <Button
          v-else
          label="Закрыть приложение"
          icon="pi pi-times"
          size="large"
          @click="closeApp"
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
    </div>
  </div>
</template>
