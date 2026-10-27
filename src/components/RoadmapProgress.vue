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
  <div class="flex flex-col" :class="compact ? 'gap-1.5' : 'gap-2'">
    <div class="flex items-baseline justify-between gap-2">
      <span class="font-semibold" :class="compact ? 'text-meta' : 'text-md'">{{ label }}</span>
      <span class="text-meta text-muted-color">
        <strong class="font-semibold text-color">{{ done }}</strong> из {{ total }}{{ compact ? '' : ' проектов' }}
      </span>
    </div>
    <div
      class="grid gap-1"
      role="img"
      :aria-label="`${label}: сдано ${done} из ${total} проектов`"
      :style="{ gridTemplateColumns: `repeat(${total}, minmax(0, 1fr))` }"
    >
      <span
        v-for="(step, index) in steps"
        :key="index"
        class="h-2 rounded-sm"
        :class="step ? 'bg-(--p-roadmap-segment-filled-background)' : 'bg-(--p-roadmap-segment-background)'"
      />
    </div>
  </div>
</template>
