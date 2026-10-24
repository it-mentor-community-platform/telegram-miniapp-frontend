<script setup lang="ts">
import Tag from 'primevue/tag'
import { RouterLink, type RouteLocationRaw } from 'vue-router'

withDefaults(
  defineProps<{
    icon: string
    title: string
    subtitle: string
    badge?: string
    badgeTone?: 'success' | 'neutral'
    to?: RouteLocationRaw
    divider?: boolean
  }>(),
  { badgeTone: 'success' },
)
</script>

<template>
  <component
    :is="to ? RouterLink : 'div'"
    :to="to"
    class="nav-list-row"
    :class="{ divider, interactive: to }"
  >
    <span class="row-icon" aria-hidden="true"><i :class="['pi', icon]" /></span>
    <span class="row-text">
      <span class="row-title">{{ title }}</span>
      <span class="row-subtitle">{{ subtitle }}</span>
    </span>
    <Tag
      v-if="badge"
      :value="badge"
      :severity="badgeTone === 'neutral' ? 'secondary' : 'success'"
      class="row-badge"
    />
    <i class="pi pi-chevron-right row-chevron" aria-hidden="true" />
  </component>
</template>

<style scoped>
.nav-list-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 4rem;
  padding: 0.75rem 1rem;
  color: var(--p-text-color);
  text-decoration: none;
}

.nav-list-row.divider {
  border-top: 1px solid var(--p-content-border-color);
}

.nav-list-row.interactive:hover {
  background: var(--p-content-hover-background);
}

.nav-list-row.interactive:focus-visible {
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
  color: var(--p-surface-700);
  font-size: 1.125rem;
}

.app-dark .row-icon {
  background: var(--p-surface-800);
  color: var(--p-surface-300);
}

.row-text {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.row-title {
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.25rem;
}

.row-subtitle {
  color: var(--p-text-muted-color);
  font-size: 0.8125rem;
  line-height: 1.125rem;
}

.row-badge {
  white-space: nowrap;
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
