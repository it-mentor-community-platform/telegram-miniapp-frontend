<script setup lang="ts">
import type { ProjectIcon } from '../roadmap'

// Project type icon, drawn from design/ProjectRow.dc.html. An exception to "PrimeIcons only":
// PrimeIcons has no gallows, sprout, tennis ball or calendar-check. Colored by currentColor.
defineProps<{
  icon: ProjectIcon
}>()
</script>

<template>
  <svg
    class="size-5"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <template v-if="icon === 'hangman'">
      <path d="M4 21h10" />
      <path d="M7 21V3h8v3" />
      <circle cx="15" cy="8.5" r="2.5" />
      <path d="M15 11v5M12.5 13h5M15 16l-2 3M15 16l2 3" />
    </template>
    <template v-else-if="icon === 'simulation'">
      <path d="M12 21v-8" />
      <path d="M12 13c0-4 3-7 8-7 0 5-3 8-8 7z" />
      <path d="M12 15.5c0-3-2.5-5.5-7-5.5 0 4 2.5 6 7 5.5z" />
    </template>
    <template v-else-if="icon === 'exchange'">
      <path d="M4 8h14l-3.5-3.5" />
      <path d="M20 16H6l3.5 3.5" />
    </template>
    <template v-else-if="icon === 'tennis'">
      <circle cx="12" cy="12" r="9" />
      <path d="M5.6 5.6a9 9 0 0 1 0 12.8" />
      <path d="M18.4 5.6a9 9 0 0 0 0 12.8" />
    </template>
    <template v-else-if="icon === 'cloud'">
      <path d="M7 18.5h10a4 4 0 0 0 .6-7.96A6 6 0 0 0 6.1 9.6 4.5 4.5 0 0 0 7 18.5z" />
    </template>
    <template v-else-if="icon === 'planner'">
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M3 10h18M8 3v4M16 3v4" />
      <path d="m9 15 2 2 4-4" />
    </template>
  </svg>
</template>
