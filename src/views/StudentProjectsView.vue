<script setup lang="ts">
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
  <div class="projects">
    <Breadcrumbs :items="breadcrumbs" />
    <h1 class="projects-title">Мои проекты</h1>

    <section v-if="tracks.length > 0" class="progress-card" aria-label="Прогресс по роадмапам">
      <div v-for="track in completedTracks" :key="track.language" class="completed-banner">
        <span class="completed-icon" aria-hidden="true"><i class="pi pi-trophy" /></span>
        <span class="completed-text">
          <span class="completed-title">Роадмап {{ track.label }} пройден</span>
          <span class="completed-body">
            Все 6 проектов сданы. Новые реализации можно добавлять и дальше — например, на другом
            языке.
          </span>
        </span>
      </div>
      <RoadmapProgress
        v-for="track in tracks"
        :key="track.language"
        :label="track.label"
        :steps="track.steps"
      />
      <p class="progress-note">
        В прогрессе учитываются реализации на Java, Python и Go. Несколько реализаций одного проекта
        на одном языке — один шаг.
      </p>
    </section>

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
        <p class="untracked-note">
          <LanguageTag
            v-for="language in untrackedLanguages"
            :key="language"
            :label="language"
            :counted="false"
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

<style scoped>
.projects {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.projects-title {
  margin: 0;
  font-size: 1.375rem;
  font-weight: 700;
  line-height: 1.75rem;
}

.progress-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--p-content-border-color);
  border-radius: var(--p-content-border-radius);
  background: var(--p-content-background);
  box-shadow: 0 1px 2px rgb(15 23 42 / 0.04);
}

.app-dark .progress-card {
  box-shadow: none;
}

.completed-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.625rem;
  background: var(--p-emerald-50);
}

.app-dark .completed-banner {
  background: color-mix(in srgb, var(--p-emerald-400) 16%, transparent);
}

.completed-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: var(--p-primary-color);
  color: var(--p-primary-contrast-color);
  font-size: 1.125rem;
}

.completed-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.completed-title {
  color: var(--p-emerald-700);
  font-size: 0.9375rem;
  font-weight: 700;
  line-height: 1.25rem;
}

.app-dark .completed-title {
  color: var(--p-emerald-300);
}

.completed-body {
  color: var(--p-surface-700);
  font-size: 0.8125rem;
  line-height: 1.125rem;
}

.app-dark .completed-body {
  color: var(--p-surface-300);
}

.progress-note {
  margin: 0;
  padding-top: 0.75rem;
  border-top: 1px solid var(--p-content-border-color);
  color: var(--p-text-muted-color);
  font-size: 0.75rem;
  line-height: 1.0625rem;
}

.untracked-note {
  margin: 0;
  padding: 0 0.25rem;
  color: var(--p-text-muted-color);
  font-size: 0.75rem;
  line-height: 1.0625rem;
}

.untracked-note .language-tag {
  margin-right: 0.25rem;
}
</style>
