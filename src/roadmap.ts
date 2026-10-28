// Roadmap facts shared by screens: the fixed project types and the languages that count toward
// progress (see meta/business-analytics/functionality/student-roadmap-completion.md).

import type { ProjectsSummaryDto, RoadmapProjectDto } from './api'

// Project types are identified by project-service's keys. Its WEATHER_VIEWER and OTHER are not
// part of the six-project roadmap and are ignored.
export type ProjectTypeId = Exclude<RoadmapProjectDto, 'WEATHER_VIEWER' | 'OTHER'>

// Readable `:projectType` URL segment (design/README.md → Routes); used only in routes.
export type ProjectTypeSlug =
  | 'hangman'
  | 'simulation'
  | 'currency-exchange'
  | 'tennis-scoreboard'
  | 'cloud-storage'
  | 'task-scheduler'

export type ProjectIcon = 'hangman' | 'simulation' | 'exchange' | 'tennis' | 'cloud' | 'planner'

export type ProjectType = {
  id: ProjectTypeId
  slug: ProjectTypeSlug
  title: string
  icon: ProjectIcon
}

export type RoadmapTrack = {
  language: string
  label: string
  steps: boolean[]
}

// Languages a student has submitted implementations in, per project type.
export type LanguagesByProjectType = Record<ProjectTypeId, readonly string[]>

// In roadmap order.
export const PROJECT_TYPES: ProjectType[] = [
  { id: 'HANGMAN', slug: 'hangman', title: 'Виселица', icon: 'hangman' },
  { id: 'SIMULATION', slug: 'simulation', title: 'Симуляция', icon: 'simulation' },
  { id: 'CURRENCY_EXCHANGE', slug: 'currency-exchange', title: 'Обмен валют', icon: 'exchange' },
  { id: 'TENNIS_SCOREBOARD', slug: 'tennis-scoreboard', title: 'Теннисное табло', icon: 'tennis' },
  { id: 'CLOUD_FILE_STORAGE', slug: 'cloud-storage', title: 'Облачное хранилище', icon: 'cloud' },
  { id: 'TASK_TRACKER', slug: 'task-scheduler', title: 'Планировщик задач', icon: 'planner' },
]

export const TRACKED_LANGUAGES = ['Java', 'Python', 'Go']

export function isTracked(language: string) {
  return TRACKED_LANGUAGES.includes(language)
}

// One track per tracked language with at least one completed step; several implementations of
// one project type in the same language count as one step.
export function buildRoadmapTracks(languagesByType: LanguagesByProjectType): RoadmapTrack[] {
  return TRACKED_LANGUAGES.map((language) => ({
    language,
    label: `${language} Backend`,
    steps: PROJECT_TYPES.map((type) => languagesByType[type.id].includes(language)),
  })).filter((track) => track.steps.some(Boolean))
}

// Keeps the six roadmap project types; ones without implementations get an empty list.
export function toLanguagesByProjectType(summary: ProjectsSummaryDto): LanguagesByProjectType {
  return {
    HANGMAN: summary.HANGMAN ?? [],
    SIMULATION: summary.SIMULATION ?? [],
    CURRENCY_EXCHANGE: summary.CURRENCY_EXCHANGE ?? [],
    TENNIS_SCOREBOARD: summary.TENNIS_SCOREBOARD ?? [],
    CLOUD_FILE_STORAGE: summary.CLOUD_FILE_STORAGE ?? [],
    TASK_TRACKER: summary.TASK_TRACKER ?? [],
  }
}
