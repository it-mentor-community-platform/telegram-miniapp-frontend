<script setup lang="ts">
import Tag from 'primevue/tag'

defineProps<{
  label: string
  counted: boolean
}>()
</script>

<template>
  <Tag
    :value="label"
    class="rounded-md border px-1.5 py-0"
    :class="
      counted
        ? 'tint-neutral border-transparent'
        : 'border-dashed border-(--p-subtle-color) bg-transparent text-muted-color'
    "
    :aria-label="counted ? label : `${label} — не учитывается в прогрессе`"
  />
</template>
