<script setup lang="ts">
import { computed } from 'vue'
import Avatar from 'primevue/avatar'
import Skeleton from 'primevue/skeleton'
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import type { ProjectIcon } from '../roadmap'
import LanguageTag from './LanguageTag.vue'

const props = defineProps<{
  icon: ProjectIcon
  title: string
  langs: { name: string; counted: boolean }[]
  to?: RouteLocationRaw
  divider?: boolean
  // Whether langs is known: 'loading' shows a placeholder status line, 'unknown' (load failed) none.
  status?: 'loaded' | 'loading' | 'unknown'
}>()

const loaded = computed(() => (props.status ?? 'loaded') === 'loaded')
const submitted = computed(() => loaded.value && props.langs.length > 0)

// Closest PrimeIcons to the design's per-project icons.
const icons: Record<ProjectIcon, string> = {
  hangman: 'pi-question',
  simulation: 'pi-sparkles',
  exchange: 'pi-arrow-right-arrow-left',
  tennis: 'pi-stopwatch',
  cloud: 'pi-cloud',
  planner: 'pi-calendar-clock',
}
</script>

<template>
  <component
    :is="to ? RouterLink : 'div'"
    :to="to"
    class="flex min-h-18 items-center gap-3 px-4 py-3 text-color"
    :class="{ 'border-t border-surface': divider, 'focus-ring hover:bg-emphasis': to }"
  >
    <Avatar
      :icon="`pi ${icons[icon]}`"
      class="shrink-0"
      :class="submitted ? 'bg-primary text-primary-contrast' : 'text-muted-color'"
      aria-hidden="true"
    />
    <span class="flex min-w-0 flex-1 flex-col gap-1.5">
      <span class="text-md font-semibold">{{ title }}</span>
      <Skeleton v-if="status === 'loading'" width="7rem" height="0.875rem" aria-hidden="true" />
      <span v-else-if="submitted" class="flex flex-wrap items-center gap-1.5">
        <span class="inline-flex items-center gap-1 text-xs font-semibold text-(--p-tint-success-color)">
          <i class="pi pi-check text-xs" aria-hidden="true" />Сдан
        </span>
        <LanguageTag v-for="lang in langs" :key="lang.name" :label="lang.name" :counted="lang.counted" />
      </span>
      <span v-else-if="loaded" class="text-xs font-medium text-muted-color">Не сдан</span>
    </span>
    <i class="pi pi-chevron-right shrink-0 text-sm text-subtle-color" aria-hidden="true" />
  </component>
</template>
