<script setup lang="ts">
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import { RouterLink, type RouteLocationRaw } from 'vue-router'

// Full-page "not found" for an unknown URL parameter (design/ProjectType-NotFound.dc.html). The URL
// stays as typed, so Telegram's back button still works.
defineProps<{
  title: string
  text: string
  action: { label: string; to: RouteLocationRaw }
}>()
</script>

<template>
  <div class="flex flex-1 flex-col items-center justify-center gap-4 pb-20 text-center md:flex-none md:pt-18">
    <Avatar
      icon="pi pi-search"
      shape="circle"
      class="size-16 text-muted-color"
      :dt="{ icon: { size: '1.75rem' } }"
      aria-hidden="true"
    />
    <div class="flex max-w-75 flex-col gap-1.5">
      <h1 class="text-page font-bold">{{ title }}</h1>
      <p class="text-md/[1.375rem] text-muted-color">{{ text }}</p>
    </div>
    <Button :as="RouterLink" :to="action.to" :label="action.label" size="large" />
  </div>
</template>
