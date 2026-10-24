<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  steps: boolean[]
  compact?: boolean
}>()

const done = computed(() => props.steps.filter(Boolean).length)
const total = computed(() => props.steps.length)
</script>

<template>
  <div class="roadmap-progress" :class="{ compact }">
    <div class="roadmap-header">
      <span class="roadmap-label">{{ label }}</span>
      <span class="roadmap-count">
        <strong>{{ done }}</strong> из {{ total }}{{ compact ? '' : ' проектов' }}
      </span>
    </div>
    <div
      class="roadmap-segments"
      role="img"
      :aria-label="`${label}: сдано ${done} из ${total} проектов`"
      :style="{ gridTemplateColumns: `repeat(${total}, minmax(0, 1fr))` }"
    >
      <span v-for="(step, index) in steps" :key="index" class="segment" :class="{ filled: step }" />
    </div>
  </div>
</template>

<style scoped>
.roadmap-progress {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.roadmap-progress.compact {
  gap: 0.375rem;
}

.roadmap-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.roadmap-label {
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.25rem;
}

.compact .roadmap-label {
  font-size: 0.8125rem;
}

.roadmap-count {
  color: var(--p-text-muted-color);
  font-size: 0.8125rem;
  line-height: 1.125rem;
}

.roadmap-count strong {
  color: var(--p-text-color);
  font-weight: 600;
}

.roadmap-segments {
  display: grid;
  gap: 0.25rem;
}

.segment {
  height: 0.5rem;
  border-radius: 0.25rem;
  background: var(--p-content-border-color);
}

.segment.filled {
  background: var(--p-emerald-500);
}

.app-dark .segment {
  background: var(--p-surface-700);
}

.app-dark .segment.filled {
  background: var(--p-emerald-400);
}
</style>
