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
  <Breadcrumb
    :home="home"
    :model="model"
    aria-label="Навигация"
    class="breadcrumbs"
    :dt="{ padding: '0', background: 'transparent', gap: '0' }"
  >
    <template #item="{ item }">
      <RouterLink :to="item.route" class="crumb-link" :aria-label="item.ariaLabel">
        <i v-if="item.icon" :class="item.icon" aria-hidden="true" />
        <span v-else class="crumb-label">{{ item.label }}</span>
      </RouterLink>
    </template>
  </Breadcrumb>
</template>

<style scoped>
/* The home icon's tap target extends into the page gutter so that the icon lines up with the content. */
.breadcrumbs {
  margin: -0.75rem 0 -0.625rem -0.75rem;
  min-width: 0;
}

.breadcrumbs :deep(.p-breadcrumb-list) {
  flex-wrap: nowrap;
  min-width: 0;
}

.breadcrumbs :deep(.p-breadcrumb-item) {
  min-width: 0;
}

.breadcrumbs :deep(.p-breadcrumb-item:last-child) {
  flex-shrink: 1;
}

.breadcrumbs :deep(.p-breadcrumb-separator) {
  flex-shrink: 0;
  color: var(--p-surface-400);
}

.crumb-link {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.75rem;
  height: 2.75rem;
  padding: 0 0.5rem;
  border-radius: var(--p-content-border-radius);
  color: var(--p-text-muted-color);
  font-size: 0.8125rem;
  font-weight: 500;
  text-decoration: none;
}

.crumb-link:focus-visible {
  outline: 2px solid var(--p-primary-color);
  outline-offset: -2px;
}

.crumb-link .pi {
  font-size: 1.125rem;
}

.crumb-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
