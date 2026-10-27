<script setup lang="ts">
import Avatar from 'primevue/avatar'
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
    class="flex min-h-16 items-center gap-3 px-4 py-3 text-color"
    :class="{ 'border-t border-surface': divider, 'focus-ring hover:bg-emphasis': to }"
  >
    <Avatar :icon="`pi ${icon}`" class="shrink-0" aria-hidden="true" />
    <span class="flex min-w-0 flex-1 flex-col gap-0.5">
      <span class="text-md font-semibold">{{ title }}</span>
      <span class="text-meta text-muted-color">{{ subtitle }}</span>
    </span>
    <Tag
      v-if="badge"
      :value="badge"
      :severity="badgeTone === 'neutral' ? 'secondary' : 'success'"
      class="whitespace-nowrap"
    />
    <i class="pi pi-chevron-right shrink-0 text-sm text-subtle-color" aria-hidden="true" />
  </component>
</template>
