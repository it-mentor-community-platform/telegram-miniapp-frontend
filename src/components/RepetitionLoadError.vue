<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'

defineProps<{ text: string; loading?: boolean; disabled?: boolean }>()
defineEmits<{ retry: [] }>()
</script>

<template>
  <Message severity="error" class="rounded-xl border-(--p-tint-error-border-color) bg-(--p-tint-error-background) text-(--p-tint-error-color) shadow-none" :pt="{ content: { class: 'px-4 py-3.5' }, text: { class: 'w-full' } }">
    <div class="flex flex-col items-start gap-3">
      <div class="flex items-start gap-2.5 text-sm font-normal">
        <i class="pi pi-exclamation-circle mt-0.5 shrink-0 text-lg" aria-hidden="true" />
        <span>{{ text }}</span>
      </div>
      <Button label="Попробовать снова" icon="pi pi-refresh" severity="danger" variant="outlined" size="small" class="min-h-10 border-(--p-tint-error-border-color) bg-(--p-content-background) text-(--p-tint-error-color)" :loading="loading" :disabled="disabled" @click="$emit('retry')" />
    </div>
  </Message>
</template>
