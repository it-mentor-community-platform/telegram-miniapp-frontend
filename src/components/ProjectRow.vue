<script setup lang="ts">
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import type { ProjectIcon } from '../roadmap'
import LanguageTag from './LanguageTag.vue'

defineProps<{
  icon: ProjectIcon
  title: string
  langs: { name: string; counted: boolean }[]
  to?: RouteLocationRaw
  divider?: boolean
}>()

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
    class="project-row"
    :class="{ divider, interactive: to }"
  >
    <span class="row-icon" :class="{ done: langs.length > 0 }" aria-hidden="true">
      <i :class="['pi', icons[icon]]" />
    </span>
    <span class="row-text">
      <span class="row-title">{{ title }}</span>
      <span v-if="langs.length > 0" class="row-status">
        <span class="row-done"><i class="pi pi-check" aria-hidden="true" />Сдан</span>
        <LanguageTag v-for="lang in langs" :key="lang.name" :label="lang.name" :counted="lang.counted" />
      </span>
      <span v-else class="row-not-done">Не сдан</span>
    </span>
    <i class="pi pi-chevron-right row-chevron" aria-hidden="true" />
  </component>
</template>

<style scoped>
.project-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 4.5rem;
  padding: 0.75rem 1rem;
  color: var(--p-text-color);
  text-decoration: none;
}

.project-row.divider {
  border-top: 1px solid var(--p-content-border-color);
}

.project-row.interactive:hover {
  background: var(--p-content-hover-background);
}

.project-row.interactive:focus-visible {
  outline: 2px solid var(--p-primary-color);
  outline-offset: -2px;
}

.row-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.625rem;
  background: var(--p-surface-100);
  color: var(--p-text-muted-color);
  font-size: 1.125rem;
}

.app-dark .row-icon {
  background: var(--p-surface-800);
}

.row-icon.done,
.app-dark .row-icon.done {
  background: var(--p-primary-color);
  color: var(--p-primary-contrast-color);
}

.row-text {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 0;
}

.row-title {
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.25rem;
}

.row-status {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.375rem;
}

.row-done {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--p-emerald-700);
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1rem;
}

.app-dark .row-done {
  color: var(--p-emerald-300);
}

.row-done .pi {
  font-size: 0.75rem;
}

.row-not-done {
  color: var(--p-text-muted-color);
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1rem;
}

.row-chevron {
  flex-shrink: 0;
  color: var(--p-surface-400);
  font-size: 0.875rem;
}

.app-dark .row-chevron {
  color: var(--p-surface-500);
}
</style>
