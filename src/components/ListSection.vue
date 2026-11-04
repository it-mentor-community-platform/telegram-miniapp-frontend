<script setup lang="ts">
import { useId } from 'vue'
import Card from 'primevue/card'

defineProps<{
  title: string
  // From md up, the rows become separate tiles in a grid: 2 columns, and this many on desktop (lg).
  tiles?: 2 | 3
}>()

const titleId = useId()
</script>

<template>
  <section class="flex flex-col gap-2" :aria-labelledby="titleId">
    <h2 :id="titleId" class="px-1 text-meta font-semibold tracking-[0.04em] text-muted-color uppercase">
      {{ title }}
    </h2>
    <!-- Rows run edge to edge and draw their own dividers. As tiles, the card itself disappears and
         each row gets the card look instead. -->
    <Card
      class="overflow-hidden"
      :class="{ 'md:overflow-visible md:border-0 md:bg-transparent md:shadow-none': tiles }"
      :pt="{ body: { class: 'p-0' } }"
    >
      <template #content>
        <nav
          class="flex flex-col"
          :class="tiles && ['md:grid md:grid-cols-2 md:gap-3 md:*:tile', { 'lg:grid-cols-3': tiles === 3 }]"
        >
          <slot />
        </nav>
      </template>
    </Card>
    <slot name="footer" />
  </section>
</template>
