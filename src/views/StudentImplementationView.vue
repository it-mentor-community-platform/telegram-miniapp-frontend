<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import { useBreadcrumbs } from '../composables/useBreadcrumbs'
import ImplementationNotFound from './implementation/ImplementationNotFound.vue'
import ImplementationPage from './implementation/ImplementationPage.vue'

const route = useRoute()
const breadcrumbs = useBreadcrumbs()

// Backend IDs are positive integers; anything else is not found without a request.
const id = computed(() => {
  const param = String(route.params.implementationId)
  return /^\d+$/.test(param) ? Number(param) : undefined
})
</script>

<template>
  <div class="flex flex-1 flex-col gap-4">
    <Breadcrumbs :items="breadcrumbs" />
    <ImplementationPage v-if="id" :key="id" :id="id" />
    <ImplementationNotFound v-else />
  </div>
</template>
