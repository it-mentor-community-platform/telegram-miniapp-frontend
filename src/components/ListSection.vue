<script setup lang="ts">
import { useId } from 'vue'
import Card from 'primevue/card'

defineProps<{
  title: string
}>()

const titleId = useId()
</script>

<template>
  <section class="flex flex-col gap-2" :aria-labelledby="titleId">
    <h2 :id="titleId" class="px-1 text-meta font-semibold tracking-[0.04em] text-muted-color uppercase">
      {{ title }}
    </h2>
    <!-- Rows run edge to edge and draw their own dividers. -->
    <Card class="overflow-hidden" :pt="{ body: { class: 'p-0' } }">
      <template #content>
        <nav class="flex flex-col">
          <slot />
        </nav>
      </template>
    </Card>
    <slot name="footer" />
  </section>
</template>
