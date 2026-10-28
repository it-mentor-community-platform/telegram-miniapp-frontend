<script setup lang="ts">
import { computed } from 'vue'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import EmptyState from '../components/EmptyState.vue'
import LanguageTag from '../components/LanguageTag.vue'
import ListSection from '../components/ListSection.vue'
import ProjectRow from '../components/ProjectRow.vue'
import RoadmapProgress from '../components/RoadmapProgress.vue'
import { useBreadcrumbs } from '../composables/useBreadcrumbs'
import { useMyProjects } from '../composables/useMyProjects'
import { buildRoadmapTracks, isTracked, joinRussian, PROJECT_TYPES, toLanguagesByProjectType } from '../roadmap'

const breadcrumbs = useBreadcrumbs()
const { languagesByType: loaded, loading, failed, load } = useMyProjects()
load()

// Status of the project list rows; 'unknown' once the first load failed (until a retry starts).
const loadStatus = computed(() =>
  loaded.value ? 'loaded' : failed.value && !loading.value ? 'unknown' : 'loading',
)

// Until the first response, an empty set: the rows still render, with a placeholder status.
const languagesByType = computed(() => loaded.value ?? toLanguagesByProjectType({}))

const tracks = computed(() => buildRoadmapTracks(languagesByType.value))
const completedTracks = computed(() => tracks.value.filter((track) => track.steps.every(Boolean)))
const projects = computed(() =>
  PROJECT_TYPES.map((type) => ({
    ...type,
    langs: languagesByType.value[type.id].map((name) => ({ name, counted: isTracked(name) })),
  })),
)

const allLanguages = computed(() => [...new Set(Object.values(languagesByType.value).flat())])
const untrackedLanguages = computed(() => allLanguages.value.filter((language) => !isTracked(language)))
const isEmpty = computed(() => allLanguages.value.length === 0)
const onlyUntracked = computed(() => !isEmpty.value && tracks.value.length === 0)

const untrackedText = computed(
  () =>
    `Ваши проекты сданы на ${joinRussian(untrackedLanguages.value)}. ` +
    'В прогресс роадмапов засчитываются реализации на Java, Python и Go.',
)
</script>

<template>
  <div class="flex flex-col gap-4">
    <Breadcrumbs :items="breadcrumbs" />
    <h1 class="text-page font-bold">Мои проекты</h1>

    <!-- Until the first response: design/Projects-Loading.dc.html, Projects-Error.dc.html. Later
         visits show the last data while it refreshes. -->
    <Card v-if="loadStatus === 'loading'" aria-busy="true" aria-label="Загрузка прогресса">
      <template #content>
        <div class="flex flex-col gap-4" aria-hidden="true">
          <div v-for="width in ['7rem', '8rem']" :key="width" class="flex flex-col gap-2.5">
            <div class="flex items-center justify-between">
              <Skeleton :width="width" height="1rem" />
              <Skeleton width="5.75rem" height="0.875rem" />
            </div>
            <Skeleton height="0.5rem" />
          </div>
          <div class="flex flex-col gap-1.5 border-t border-surface pt-3">
            <Skeleton height="0.75rem" />
            <Skeleton width="70%" height="0.75rem" />
          </div>
        </div>
      </template>
    </Card>

    <Message v-else-if="loadStatus === 'unknown'" severity="error" icon="pi pi-exclamation-circle" role="alert">
      <div class="flex flex-col items-start gap-3">
        <span>Не удалось загрузить проекты. Проверьте соединение и попробуйте ещё раз.</span>
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

    <template v-else>
      <Card v-if="tracks.length > 0" role="region" aria-label="Прогресс по роадмапам">
        <template #content>
          <div class="flex flex-col gap-4">
            <div
              v-for="track in completedTracks"
              :key="track.language"
              class="tint-success flex items-start gap-3 rounded-[0.625rem] p-3"
            >
              <Avatar
                icon="pi pi-trophy"
                shape="circle"
                class="size-9 shrink-0 bg-primary text-primary-contrast"
                aria-hidden="true"
              />
              <span class="flex flex-col gap-0.5">
                <span class="text-md font-bold">Роадмап {{ track.label }} пройден</span>
                <span class="text-meta text-(--p-tint-neutral-color)">
                  Все 6 проектов сданы. Новые реализации можно добавлять и дальше — например, на
                  другом языке.
                </span>
              </span>
            </div>
            <RoadmapProgress
              v-for="track in tracks"
              :key="track.language"
              :label="track.label"
              :steps="track.steps"
            />
            <p class="border-t border-surface pt-3 text-note text-muted-color">
              В прогрессе учитываются реализации на Java, Python и Go. Несколько реализаций одного
              проекта на одном языке — один шаг.
            </p>
          </div>
        </template>
      </Card>

      <EmptyState
        v-if="isEmpty"
        icon="none"
        title="Здесь появится ваш прогресс"
        text="Выберите любой проект и сдайте ссылку на публичный GitHub-репозиторий. Прогресс считается отдельно для Java, Python и Go роадмапов."
      />
      <EmptyState
        v-if="onlyUntracked"
        icon="info"
        title="Прогресс по роадмапам пока не считается"
        :text="untrackedText"
      />
    </template>

    <ListSection title="Проекты роадмапа">
      <ProjectRow
        v-for="(project, index) in projects"
        :key="project.id"
        :icon="project.icon"
        :title="project.title"
        :langs="project.langs"
        :divider="index > 0"
        :status="loadStatus"
        :to="{ name: 'student-project', params: { projectType: project.slug } }"
      />
      <template v-if="tracks.length > 0 && untrackedLanguages.length > 0" #footer>
        <p class="px-1 text-note text-muted-color">
          <LanguageTag
            v-for="language in untrackedLanguages"
            :key="language"
            :label="language"
            :counted="false"
            class="mr-1"
          />
          {{
            untrackedLanguages.length > 1
              ? '— языки вне роадмапов, в прогрессе не учитываются'
              : '— язык вне роадмапов, в прогрессе не учитывается'
          }}
        </p>
      </template>
    </ListSection>
  </div>
</template>
