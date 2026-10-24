<script setup lang="ts">
import { RouterLink, type RouteLocationRaw } from 'vue-router'

defineProps<{
  icon: string
  title: string
  subtitle: string
  to?: RouteLocationRaw
}>()
</script>

<template>
  <component :is="to ? RouterLink : 'div'" :to="to" class="section-card" :class="{ interactive: to }">
    <div class="card-header">
      <span class="card-icon" aria-hidden="true"><i :class="['pi', icon]" /></span>
      <span class="card-text">
        <span class="card-title">{{ title }}</span>
        <span class="card-subtitle">{{ subtitle }}</span>
      </span>
      <i class="pi pi-chevron-right card-chevron" aria-hidden="true" />
    </div>
    <slot />
  </component>
</template>

<style scoped>
.section-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--p-content-border-color);
  border-radius: var(--p-content-border-radius);
  background: var(--p-content-background);
  box-shadow: 0 1px 2px rgb(15 23 42 / 0.04);
  color: var(--p-text-color);
  text-decoration: none;
}

.app-dark .section-card {
  box-shadow: none;
}

.section-card.interactive:focus-visible {
  outline: 2px solid var(--p-primary-color);
  outline-offset: 2px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.card-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.625rem;
  background: var(--p-emerald-50);
  color: var(--p-emerald-700);
  font-size: 1.25rem;
}

.app-dark .card-icon {
  background: color-mix(in srgb, var(--p-emerald-400) 16%, transparent);
  color: var(--p-emerald-300);
}

.card-text {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.25rem;
}

.card-subtitle {
  color: var(--p-text-muted-color);
  font-size: 0.8125rem;
  line-height: 1.125rem;
}

.card-chevron {
  flex-shrink: 0;
  color: var(--p-surface-400);
  font-size: 0.875rem;
}

.app-dark .card-chevron {
  color: var(--p-surface-500);
}
</style>
