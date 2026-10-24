<script setup lang="ts">
import type { StatItem } from '../mocks/home'

defineProps<{
  items: StatItem[]
}>()
</script>

<template>
  <div class="stat-tiles">
    <div v-for="item in items" :key="item.label" class="stat-tile" :class="`tone-${item.tone}`">
      <span class="stat-value">{{ item.value }}</span>
      <span class="stat-label">{{ item.label }}</span>
    </div>
  </div>
</template>

<style scoped>
.stat-tiles {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
}

.stat-tile {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  background: var(--tile-bg);
  color: var(--tile-fg);
}

.stat-value {
  color: var(--tile-value, var(--tile-fg));
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.5rem;
}

.stat-label {
  font-size: 0.75rem;
  line-height: 1rem;
}

.tone-warn {
  --tile-bg: var(--p-orange-50);
  --tile-fg: var(--p-orange-700);
}

.tone-info {
  --tile-bg: var(--p-blue-50);
  --tile-fg: var(--p-blue-700);
}

.tone-success {
  --tile-bg: var(--p-emerald-50);
  --tile-fg: var(--p-emerald-700);
}

.tone-neutral {
  --tile-bg: var(--p-surface-100);
  --tile-fg: var(--p-text-muted-color);
  --tile-value: var(--p-text-color);
}

.app-dark .tone-warn {
  --tile-bg: color-mix(in srgb, var(--p-orange-500) 16%, transparent);
  --tile-fg: var(--p-orange-300);
}

.app-dark .tone-info {
  --tile-bg: color-mix(in srgb, var(--p-blue-400) 16%, transparent);
  --tile-fg: var(--p-blue-300);
}

.app-dark .tone-success {
  --tile-bg: color-mix(in srgb, var(--p-emerald-400) 16%, transparent);
  --tile-fg: var(--p-emerald-300);
}

.app-dark .tone-neutral {
  --tile-bg: var(--p-surface-800);
}
</style>
