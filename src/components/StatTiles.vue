<script setup lang="ts">
import type { StatItem, StatTone } from '../mocks/home'

defineProps<{
  items: StatItem[]
}>()

const tones: Record<StatTone, string> = {
  warn: 'tint-warn',
  info: 'tint-info',
  success: 'tint-success',
  neutral: 'bg-(--p-tint-neutral-background) text-muted-color',
}
</script>

<template>
  <div class="grid grid-cols-3 gap-2">
    <div
      v-for="item in items"
      :key="item.label"
      class="flex flex-col gap-0.5 rounded-lg px-3 py-2.5"
      :class="tones[item.tone]"
    >
      <span class="text-xl/6 font-bold" :class="{ 'text-color': item.tone === 'neutral' }">
        {{ item.value }}
      </span>
      <span class="text-xs">{{ item.label }}</span>
    </div>
  </div>
</template>
