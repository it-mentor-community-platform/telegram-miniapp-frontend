<script setup lang="ts">
import Avatar from 'primevue/avatar'
import Card from 'primevue/card'
import { RouterLink, type RouteLocationRaw } from 'vue-router'

defineProps<{
  icon: string
  title: string
  subtitle: string
  to?: RouteLocationRaw
}>()
</script>

<template>
  <component
    :is="to ? RouterLink : 'div'"
    :to="to"
    class="block rounded-xl text-color focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
  >
    <Card>
      <template #content>
        <div class="flex flex-col gap-4">
          <div class="flex items-center gap-3">
            <Avatar
              :icon="`pi ${icon}`"
              class="tint-success size-11 shrink-0"
              :dt="{ icon: { size: '1.25rem' } }"
              aria-hidden="true"
            />
            <span class="flex min-w-0 flex-1 flex-col gap-0.5">
              <span class="text-base/5 font-semibold">{{ title }}</span>
              <span class="text-meta text-muted-color">{{ subtitle }}</span>
            </span>
            <i class="pi pi-chevron-right shrink-0 text-sm text-subtle-color" aria-hidden="true" />
          </div>
          <slot />
        </div>
      </template>
    </Card>
  </component>
</template>
