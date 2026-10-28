<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import { RouterLink } from 'vue-router'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import { useBreadcrumbs } from '../composables/useBreadcrumbs'
import { projectTypeBySlug } from '../roadmap'
import ProjectPage from './project/ProjectPage.vue'

const route = useRoute()
const breadcrumbs = useBreadcrumbs()

// The six project types are a fixed list, so an unknown slug is resolved here, before any request.
// The URL stays as typed (design/ProjectType-NotFound.dc.html).
const projectType = computed(() => projectTypeBySlug(String(route.params.projectType)))
</script>

<template>
  <div class="flex flex-1 flex-col gap-4">
    <Breadcrumbs :items="breadcrumbs" />

    <ProjectPage v-if="projectType" :key="projectType.id" :project-type="projectType" />

    <div v-else class="flex flex-1 flex-col items-center justify-center gap-4 pb-20 text-center">
      <Avatar
        icon="pi pi-search"
        shape="circle"
        class="size-16 text-muted-color"
        :dt="{ icon: { size: '1.75rem' } }"
        aria-hidden="true"
      />
      <div class="flex max-w-75 flex-col gap-1.5">
        <h1 class="text-page font-bold">Проект не найден</h1>
        <p class="text-md/[1.375rem] text-muted-color">
          Возможно, ссылка устарела или в ней опечатка. Все проекты роадмапа — в разделе «Мои проекты».
        </p>
      </div>
      <Button :as="RouterLink" :to="{ name: 'student-projects' }" label="К моим проектам" size="large" />
    </div>
  </div>
</template>
