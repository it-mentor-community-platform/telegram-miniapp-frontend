<script setup lang="ts">
defineProps<{
  title: string
  text: string
  icon: 'info' | 'chat' | 'none'
}>()

const icons = { info: 'pi-info-circle', chat: 'pi-comment' }
</script>

<template>
  <section class="empty-state">
    <span v-if="icon !== 'none'" class="empty-icon" aria-hidden="true">
      <i :class="['pi', icons[icon]]" />
    </span>
    <span class="empty-text">
      <span class="empty-title">{{ title }}</span>
      <span class="empty-body">{{ text }}</span>
    </span>
  </section>
</template>

<style scoped>
.empty-state {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--p-content-border-color);
  border-radius: var(--p-content-border-radius);
  background: var(--p-content-background);
  color: var(--p-text-color);
}

.empty-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: var(--p-surface-100);
  color: var(--p-surface-700);
  font-size: 1.125rem;
}

.app-dark .empty-icon {
  background: var(--p-surface-800);
  color: var(--p-surface-300);
}

.empty-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.empty-title {
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.25rem;
}

.empty-body {
  color: var(--p-text-muted-color);
  font-size: 0.875rem;
  line-height: 1.25rem;
}
</style>
