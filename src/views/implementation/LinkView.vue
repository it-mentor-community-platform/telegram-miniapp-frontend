<script setup lang="ts">
import Button from 'primevue/button'

// A stored link and its edit button: the view state of the GitHub and deploy cards.
defineProps<{
  url: string
  editLabel: string
}>()

const emit = defineEmits<{ edit: [] }>()
</script>

<template>
  <div class="flex items-center gap-2">
    <a
      :href="url"
      target="_blank"
      rel="noopener"
      class="focus-ring flex min-h-11 min-w-0 flex-1 items-center gap-1.5 rounded-border text-md font-medium text-primary"
    >
      <span class="truncate">{{ url.replace(/^https?:\/\//, '') }}</span>
      <i class="pi pi-external-link shrink-0 text-xs" aria-hidden="true" />
    </a>
    <Button
      icon="pi pi-pencil"
      severity="secondary"
      variant="outlined"
      class="size-11 shrink-0"
      :aria-label="editLabel"
      @click="emit('edit')"
    />
  </div>
</template>
