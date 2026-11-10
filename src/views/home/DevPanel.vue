<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import Button from 'primevue/button'
import Panel from 'primevue/panel'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import { DEMO_IMPLEMENTATIONS, MOCK_SCENARIOS, TAKEN_GITHUB_URL } from '../../mocks/implementations'
import { projectTypeById } from '../../roadmap'
import { initData, isTelegram } from '../../telegram'

const fallbackText = 'Init data не найдена. Откройте приложение из Telegram.'

const copied = ref(false)
const textarea = useTemplateRef<{ $el: HTMLTextAreaElement }>('textarea')

// The implementation page runs on a mock API (src/mocks/implementations.ts): its demo data and
// forced corner cases.
const implementationRoute = (id: number | string, projectType: string, mock?: string): RouteLocationRaw => ({
  name: 'student-implementation',
  params: { projectType, implementationId: id },
  query: mock ? { mock } : {},
})
const [withDeploy] = DEMO_IMPLEMENTATIONS
const implementationLinks: { label: string; to: RouteLocationRaw }[] = [
  ...DEMO_IMPLEMENTATIONS.map((implementation) => ({
    label: implementation.title,
    to: implementationRoute(implementation.id, projectTypeById(implementation.roadmap_project)!.slug),
  })),
  ...Object.entries(MOCK_SCENARIOS).map(([mock, label]) => ({
    label,
    to: implementationRoute(withDeploy.id, 'currency-exchange', mock),
  })),
  { label: 'Неверный тип проекта в URL (→ редирект)', to: implementationRoute(withDeploy.id, 'hangman') },
  { label: 'Некорректный id', to: implementationRoute('abc', 'currency-exchange') },
]

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
  <Panel
    toggleable
    collapsed
    class="border-dashed border-(--p-subtle-color)"
    :dt="{ toggleableHeader: { padding: '0.5rem 0.5rem 0.5rem 1rem' }, content: { padding: '0 1rem 1rem 1rem' } }"
    :toggle-button-props="{ ariaLabel: 'Для разработчиков', severity: 'secondary', text: true, rounded: true }"
    aria-label="Инструменты разработчика"
    @toggle="copied = false"
  >
    <template #header>
      <span class="flex min-h-10 min-w-0 flex-1 items-center gap-3">
        <i class="pi pi-code shrink-0 text-lg text-(--p-tint-neutral-color)" aria-hidden="true" />
        <span class="min-w-0 flex-1 text-sm font-semibold">Для разработчиков</span>
        <Tag :severity="isTelegram ? 'success' : 'warn'" class="gap-1.5">
          <span class="size-1.5 rounded-full bg-current" aria-hidden="true" />
          {{ isTelegram ? 'Telegram' : 'Браузер' }}
        </Tag>
      </span>
    </template>
    <template #toggleicon="{ collapsed }">
      <i :class="['pi text-sm text-subtle-color', collapsed ? 'pi-chevron-down' : 'pi-chevron-up']" />
    </template>

    <div class="flex flex-col gap-2.5">
      <label class="flex flex-col gap-1.5">
        <span class="text-xs font-semibold text-(--p-tint-neutral-color)">Telegram init data</span>
        <Textarea
          ref="textarea"
          :model-value="initData || fallbackText"
          rows="5"
          readonly
          class="w-full resize-none font-mono text-note break-all"
        />
      </label>
      <div class="flex flex-wrap items-center gap-3">
        <Button label="Скопировать" icon="pi pi-copy" :disabled="!initData" @click="copyInitData" />
        <span v-if="copied" role="status" class="inline-flex items-center gap-1 text-meta font-semibold text-primary">
          <i class="pi pi-check text-xs" aria-hidden="true" />Скопировано
        </span>
      </div>
      <p class="text-note text-muted-color">
        Видно только в тестовых окружениях. Панель ничего не отправляет на сервер.
      </p>

      <div class="flex flex-col gap-1.5 border-t border-surface pt-3">
        <span class="text-xs font-semibold text-(--p-tint-neutral-color)">Страница реализации (мок API)</span>
        <ul class="flex flex-col gap-1 text-meta">
          <li v-for="link in implementationLinks" :key="link.label">
            <RouterLink :to="link.to" class="focus-ring rounded-border text-primary underline">{{ link.label }}</RouterLink>
          </li>
        </ul>
        <p class="text-note text-muted-color">
          Занятая ссылка для ответа 409: <span class="break-all">{{ TAKEN_GITHUB_URL }}</span>. Изменения
          хранятся в памяти до перезагрузки.
        </p>
      </div>
    </div>
  </Panel>
</template>
