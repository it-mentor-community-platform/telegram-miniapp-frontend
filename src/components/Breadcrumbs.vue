<script setup lang="ts">
import { computed } from 'vue'
import Breadcrumb from 'primevue/breadcrumb'
import { RouterLink } from 'vue-router'
import type { BreadcrumbItem } from '../composables/useBreadcrumbs'

const props = defineProps<{
  items: BreadcrumbItem[]
}>()

const home = { icon: 'pi pi-home', ariaLabel: 'Главная', route: { name: 'home' } }
const model = computed(() => props.items.map((item) => ({ label: item.label, route: item.to })))
</script>

<template>
  <!-- Negative margins: the home icon's tap target extends into the page gutter so that the icon
       lines up with the content. -->
  <Breadcrumb
    :home="home"
    :model="model"
    aria-label="Навигация"
    class="-mt-3 -mb-2.5 -ml-3 min-w-0"
    :dt="{ padding: '0', background: 'transparent', gap: '0' }"
    :pt="{
      list: { class: 'flex-nowrap min-w-0' },
      item: { class: 'min-w-0 last:shrink' },
      separator: { class: 'shrink-0 text-subtle-color' },
    }"
  >
    <template #item="{ item }">
      <RouterLink
        :to="item.route"
        class="focus-ring flex h-11 min-w-11 items-center justify-center rounded-border px-2 text-meta font-medium text-muted-color"
        :aria-label="item.ariaLabel"
      >
        <i v-if="item.icon" :class="[item.icon, 'text-lg']" aria-hidden="true" />
        <span v-else class="truncate">{{ item.label }}</span>
      </RouterLink>
    </template>
  </Breadcrumb>
</template>
