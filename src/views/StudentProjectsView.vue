<script setup lang="ts">
import Avatar from 'primevue/avatar'
import Card from 'primevue/card'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import EmptyState from '../components/EmptyState.vue'
import LanguageTag from '../components/LanguageTag.vue'
import ListSection from '../components/ListSection.vue'
import ProjectRow from '../components/ProjectRow.vue'
import RoadmapProgress from '../components/RoadmapProgress.vue'
import { useBreadcrumbs } from '../composables/useBreadcrumbs'
import { getMyProjects } from '../mocks/projects'
import { buildRoadmapTracks, isTracked, PROJECT_TYPES } from '../roadmap'

const breadcrumbs = useBreadcrumbs()
const languagesByType = getMyProjects()

const tracks = buildRoadmapTracks(languagesByType)
const completedTracks = tracks.filter((track) => track.steps.every(Boolean))
const projects = PROJECT_TYPES.map((type) => ({
  ...type,
  langs: languagesByType[type.slug].map((name) => ({ name, counted: isTracked(name) })),
}))

const allLanguages = [...new Set(Object.values(languagesByType).flat())]
const untrackedLanguages = allLanguages.filter((language) => !isTracked(language))
const isEmpty = allLanguages.length === 0
const onlyUntracked = !isEmpty && tracks.length === 0

const untrackedText =
  `Ваши проекты сданы на ${joinRussian(untrackedLanguages)}. ` +
  'В прогресс роадмапов засчитываются реализации на Java, Python и Go.'

function joinRussian(items: string[]) {
  return items.length > 1 ? `${items.slice(0, -1).join(', ')} и ${items.at(-1)}` : items.join('')
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <Breadcrumbs :items="breadcrumbs" />
    <h1 class="text-page font-bold">Мои проекты</h1>

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

    <ListSection title="Проекты роадмапа">
      <ProjectRow
        v-for="(project, index) in projects"
        :key="project.slug"
        :icon="project.icon"
        :title="project.title"
        :langs="project.langs"
        :divider="index > 0"
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
