<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'
import { useImplementation } from '../../composables/useImplementation'
import { isTracked, projectTypeById } from '../../roadmap'
import DeployLinkCard from './DeployLinkCard.vue'
import GithubLinkCard from './GithubLinkCard.vue'
import ImplementationNotFound from './ImplementationNotFound.vue'

// One implementation of the current student; see design/Implementation.dc.html and
// README → "Implementation page data". Reviews are not shown yet.
const props = defineProps<{
  id: number
}>()

const route = useRoute()
const router = useRouter()

const { implementation, loading, failed, notFound, load, update } = useImplementation(props.id)
load()

// Implementations of project types outside the roadmap have no page.
const projectType = computed(() => implementation.value && projectTypeById(implementation.value.projectType))

const loadState = computed(() => {
  if (notFound.value || (implementation.value && !projectType.value)) return 'not-found'
  if (implementation.value) return 'loaded'
  return failed.value && !loading.value ? 'failed' : 'loading'
})

// The URL's project type is only a readable prefix: a wrong one is replaced by the actual one.
watch(projectType, (type) => {
  if (type && type.slug !== route.params.projectType) {
    router.replace({
      name: 'student-implementation',
      params: { projectType: type.slug, implementationId: props.id },
      query: route.query,
    })
  }
})

const months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

// "12 марта 2026", as in the design.
const submittedOn = computed(() => {
  const date = implementation.value?.submittedAt
  return date && `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`
})

const details = computed(() => [
  { term: 'Тип проекта', value: projectType.value?.title },
  { term: 'Язык', value: implementation.value?.language },
  { term: 'Дата сдачи', value: submittedOn.value },
])
</script>

<template>
  <ImplementationNotFound v-if="loadState === 'not-found'" />

  <!-- Wide layouts: the header spans two columns; the cards fill the left one. The right one is
       reserved for reviews (Implementation-Desktop.dc.html), not built yet. On the phone the column
       dissolves into one stack. -->
  <div v-else class="flex flex-col gap-4 md:grid md:grid-cols-2 md:items-start md:gap-x-6">
    <header class="flex flex-col gap-1.5 md:col-span-full">
      <template v-if="implementation && projectType">
        <h1 class="text-2xl/[1.875rem] font-bold">{{ projectType.title }} · {{ implementation.language }}</h1>
        <p v-if="isTracked(implementation.language)" class="inline-flex items-center gap-1 text-meta font-semibold text-primary">
          <i class="pi pi-check text-xs" aria-hidden="true" />Засчитана в прогресс {{ implementation.language }} Backend
        </p>
        <p v-else class="text-meta font-medium text-muted-color">Не засчитывается в прогресс роадмапов</p>
      </template>
      <template v-else>
        <h1 class="sr-only">Реализация проекта</h1>
        <template v-if="loadState === 'loading'">
          <Skeleton width="15rem" height="1.875rem" />
          <Skeleton width="13rem" height="1.125rem" />
        </template>
      </template>
    </header>

    <div class="contents md:flex md:min-w-0 md:flex-col md:gap-4">
      <Message v-if="loadState === 'failed'" severity="error" icon="pi pi-exclamation-circle" role="alert">
        <div class="flex flex-col items-start gap-3">
          <span>Не удалось загрузить реализацию. Проверьте соединение и попробуйте ещё раз.</span>
          <Button
            label="Попробовать снова"
            icon="pi pi-refresh"
            severity="danger"
            variant="outlined"
            size="small"
            @click="load"
          />
        </div>
      </Message>

      <template v-else-if="loadState === 'loading'">
        <Card class="overflow-hidden" :pt="{ body: { class: 'p-0' } }" aria-busy="true" aria-label="Загрузка реализации">
          <template #content>
            <div
              v-for="(width, index) in ['6rem', '3.5rem', '7rem']"
              :key="width"
              class="flex justify-between px-4 py-3.5"
              :class="{ 'border-t border-surface': index > 0 }"
              aria-hidden="true"
            >
              <Skeleton width="5.5rem" height="0.875rem" />
              <Skeleton :width="width" height="0.875rem" />
            </div>
          </template>
        </Card>
        <Card aria-hidden="true">
          <template #content>
            <div class="flex flex-col gap-3">
              <Skeleton width="8rem" height="0.875rem" />
              <Skeleton width="80%" height="1.25rem" />
            </div>
          </template>
        </Card>
      </template>

      <template v-else-if="implementation && projectType">
        <Card class="overflow-hidden" :pt="{ body: { class: 'p-0' } }">
          <template #content>
            <dl>
              <div
                v-for="(row, index) in details"
                :key="row.term"
                class="flex justify-between gap-3 px-4 py-3 text-sm"
                :class="{ 'border-t border-surface': index > 0 }"
              >
                <dt class="text-muted-color">{{ row.term }}</dt>
                <dd class="text-right font-semibold">{{ row.value }}</dd>
              </div>
            </dl>
            <p class="flex items-center gap-1.5 bg-(--p-tint-neutral-background) px-4 py-2.5 text-note text-muted-color">
              <i class="pi pi-lock text-xs" aria-hidden="true" />
              Тип проекта и язык после сдачи изменить нельзя
            </p>
          </template>
        </Card>

        <GithubLinkCard :url="implementation.githubUrl" :save="(githubUrl) => update({ githubUrl })" />

        <DeployLinkCard
          v-if="projectType.deployable"
          :url="implementation.deployUrl"
          :save="(deployUrl) => update({ deployUrl })"
        />
      </template>
    </div>
  </div>
</template>
