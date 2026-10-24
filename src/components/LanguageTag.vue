<script setup lang="ts">
defineProps<{
  label: string
  counted: boolean
}>()
</script>

<template>
  <span
    class="language-tag"
    :class="{ uncounted: !counted }"
    :aria-label="counted ? label : `${label} — не учитывается в прогрессе`"
  >
    {{ label }}
  </span>
</template>

<style scoped>
.language-tag {
  display: inline-block;
  padding: 0 0.375rem;
  border: 1px solid var(--p-surface-100);
  border-radius: 0.375rem;
  background: var(--p-surface-100);
  color: var(--p-surface-700);
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1rem;
}

.language-tag.uncounted {
  border-style: dashed;
  border-color: var(--p-surface-400);
  background: transparent;
  color: var(--p-text-muted-color);
}

.app-dark .language-tag {
  border-color: var(--p-surface-800);
  background: var(--p-surface-800);
  color: var(--p-surface-300);
}

.app-dark .language-tag.uncounted {
  border-color: var(--p-surface-500);
  background: transparent;
  color: var(--p-text-muted-color);
}
</style>
