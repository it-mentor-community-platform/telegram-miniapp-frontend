<script setup lang="ts">
import { computed } from 'vue'
import Tag from 'primevue/tag'
import { RouterLink } from 'vue-router'
import { projectTypeById, type Implementation } from '../../roadmap'

const props = defineProps<{
  implementation: Implementation
  divider?: boolean
  // Just submitted: highlighted, fading out once `highlighted` turns false.
  highlighted?: boolean
}>()

const shortMonths = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']

// "12 мар 2026" as in the design, or "сегодня".
const submittedOn = computed(() => {
  const date = props.implementation.submittedAt
  if (date.toDateString() === new Date().toDateString()) {
    return 'сегодня'
  }
  return `${date.getDate()} ${shortMonths[date.getMonth()]} ${date.getFullYear()}`
})

// Rows are listed per roadmap project type, so the type always has a slug.
const slug = computed(() => projectTypeById(props.implementation.projectType)!.slug)

function withoutProtocol(url: string) {
  return url.replace(/^https?:\/\//, '')
}
</script>

<template>
  <RouterLink
    :to="{ name: 'student-implementation', params: { projectType: slug, implementationId: implementation.id } }"
    class="focus-ring flex items-center gap-3 px-4 py-3.5 text-color transition-colors duration-1000 hover:bg-row-hover"
    :class="{ 'border-t border-surface': divider, 'bg-(--p-tint-success-background)': highlighted }"
  >
    <span class="flex min-w-0 flex-1 flex-col gap-1.5">
      <span class="flex items-center gap-2">
        <Tag :value="implementation.language" class="tint-neutral" />
        <span class="text-meta text-muted-color">сдан {{ submittedOn }}</span>
      </span>
      <span class="flex min-w-0 items-center gap-1.5 text-sm font-medium">
        <i class="pi pi-link shrink-0 text-xs text-muted-color" aria-hidden="true" />
        <span class="truncate">{{ withoutProtocol(implementation.githubUrl) }}</span>
      </span>
      <span v-if="implementation.deployUrl" class="flex min-w-0 items-center gap-1.5 text-meta text-muted-color">
        <i class="pi pi-globe shrink-0 text-xs" aria-hidden="true" />
        <span class="truncate">{{ withoutProtocol(implementation.deployUrl) }}</span>
      </span>
    </span>
    <i class="pi pi-chevron-right shrink-0 text-sm text-subtle-color" aria-hidden="true" />
  </RouterLink>
</template>
