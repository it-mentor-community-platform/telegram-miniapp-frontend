<script setup lang="ts">
import { useId } from 'vue'

defineProps<{
  title: string
}>()

const titleId = useId()
</script>

<template>
  <section class="list-section" :aria-labelledby="titleId">
    <h2 :id="titleId" class="list-title">{{ title }}</h2>
    <nav class="list-card">
      <slot />
    </nav>
    <slot name="footer" />
  </section>
</template>

<style scoped>
.list-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-title {
  margin: 0;
  padding: 0 0.25rem;
  color: var(--p-text-muted-color);
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.125rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.list-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--p-content-border-color);
  border-radius: var(--p-content-border-radius);
  background: var(--p-content-background);
  box-shadow: 0 1px 2px rgb(15 23 42 / 0.04);
}

.app-dark .list-card {
  box-shadow: none;
}
</style>
