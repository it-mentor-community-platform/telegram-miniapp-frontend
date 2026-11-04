<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import NotFoundState from '../components/NotFoundState.vue'
import { useBreadcrumbs } from '../composables/useBreadcrumbs'
import { projectTypeBySlug } from '../roadmap'
import ProjectPage from './project/ProjectPage.vue'

const route = useRoute()
const breadcrumbs = useBreadcrumbs()

// The six project types are a fixed list, so an unknown slug is resolved here, before any request.
const projectType = computed(() => projectTypeBySlug(String(route.params.projectType)))
</script>

<template>
  <div class="flex flex-1 flex-col gap-4">
    <Breadcrumbs :items="breadcrumbs" />

    <ProjectPage v-if="projectType" :key="projectType.id" :project-type="projectType" />

    <NotFoundState
      v-else
      title="Проект не найден"
      text="Возможно, ссылка устарела или в ней опечатка. Все проекты роадмапа — в разделе «Мои проекты»."
      :action="{ label: 'К моим проектам', to: { name: 'student-projects' } }"
    />
  </div>
</template>
