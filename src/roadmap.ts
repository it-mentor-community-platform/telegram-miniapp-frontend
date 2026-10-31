// Roadmap facts shared by screens: the fixed project types and the languages that count toward
// progress (see meta/business-analytics/functionality/student-roadmap-completion.md).

import type { ProjectResponseDto, ProjectsSummaryDto, RoadmapProjectDto } from './api'

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
  // Whether an implementation can have a deploy link (web projects from currency exchange on).
  // Unused until project-service stores deploy links; the form has no deploy field until then.
  deployable: boolean
  // Page of the spec in each roadmap course: <course>/projects/<specPath>/.
  specPath: string
}

export type RoadmapTrack = {
  language: string
  label: string
  steps: boolean[]
}

// One submitted implementation of a project type by the current student.
export type Implementation = {
  id: number
  projectType: RoadmapProjectDto
  language: string
  githubUrl: string
  submittedAt: Date
}

export type NewImplementation = Pick<Implementation, 'language' | 'githubUrl'>

// Languages a student has submitted implementations in, per project type.
export type LanguagesByProjectType = Record<ProjectTypeId, readonly string[]>

// In roadmap order.
export const PROJECT_TYPES: ProjectType[] = [
  { id: 'HANGMAN', slug: 'hangman', title: 'Виселица', icon: 'hangman', deployable: false, specPath: 'hangman' },
  { id: 'SIMULATION', slug: 'simulation', title: 'Симуляция', icon: 'simulation', deployable: false, specPath: 'simulation' },
  { id: 'CURRENCY_EXCHANGE', slug: 'currency-exchange', title: 'Обмен валют', icon: 'exchange', deployable: true, specPath: 'currency-exchange' },
  { id: 'TENNIS_SCOREBOARD', slug: 'tennis-scoreboard', title: 'Теннисное табло', icon: 'tennis', deployable: true, specPath: 'tennis-scoreboard' },
  { id: 'CLOUD_FILE_STORAGE', slug: 'cloud-storage', title: 'Облачное хранилище', icon: 'cloud', deployable: true, specPath: 'cloud-file-storage' },
  { id: 'TASK_TRACKER', slug: 'task-scheduler', title: 'Планировщик задач', icon: 'planner', deployable: true, specPath: 'task-tracker' },
]

export function projectTypeBySlug(slug: string): ProjectType | undefined {
  return PROJECT_TYPES.find((type) => type.slug === slug)
}

export const TRACKED_LANGUAGES = ['Java', 'Python', 'Go']

// Roadmap course per tracked language; each project's spec is a page of it, at the same path in
// every course.
const COURSE_URLS: { language: string; url: string }[] = [
  { language: 'Java', url: 'https://zhukovsd.github.io/java-backend-learning-course/' },
  { language: 'Python', url: 'https://zhukovsd.github.io/python-backend-learning-course/' },
  { language: 'Go', url: 'https://zhukovsd.github.io/golang-backend-learning-course/' },
]

export function specLinks(type: ProjectType): { language: string; url: string }[] {
  return COURSE_URLS.map(({ language, url }) => ({ language, url: `${url}projects/${type.specPath}/` }))
}

export function isTracked(language: string) {
  return TRACKED_LANGUAGES.includes(language)
}

// Languages are free text in project-service, and the bot or importer may have stored "python":
// a tracked language in any case is spelled as on the roadmap, the rest are kept as typed.
export function canonicalLanguage(name: string) {
  const trimmed = name.trim()
  return TRACKED_LANGUAGES.find((language) => language.toLowerCase() === trimmed.toLowerCase()) ?? trimmed
}

// Canonical languages without case-insensitive repeats, in the given order; the first spelling wins.
export function uniqueLanguages(languages: readonly string[]): string[] {
  const byKey = new Map<string, string>()
  for (const language of languages.map(canonicalLanguage)) {
    if (!byKey.has(language.toLowerCase())) {
      byKey.set(language.toLowerCase(), language)
    }
  }
  return [...byKey.values()]
}

// Unique languages, tracked ones first in roadmap order, then the rest as given.
export function sortLanguages(languages: readonly string[]): string[] {
  const unique = uniqueLanguages(languages)
  return [...TRACKED_LANGUAGES.filter((language) => unique.includes(language)), ...unique.filter((language) => !isTracked(language))]
}

// "Java", "Java и Go", "Java, Python и Go".
export function joinRussian(items: readonly string[]) {
  return items.length > 1 ? `${items.slice(0, -1).join(', ')} и ${items.at(-1)}` : items.join('')
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
    HANGMAN: uniqueLanguages(summary.HANGMAN ?? []),
    SIMULATION: uniqueLanguages(summary.SIMULATION ?? []),
    CURRENCY_EXCHANGE: uniqueLanguages(summary.CURRENCY_EXCHANGE ?? []),
    TENNIS_SCOREBOARD: uniqueLanguages(summary.TENNIS_SCOREBOARD ?? []),
    CLOUD_FILE_STORAGE: uniqueLanguages(summary.CLOUD_FILE_STORAGE ?? []),
    TASK_TRACKER: uniqueLanguages(summary.TASK_TRACKER ?? []),
  }
}

export function toImplementation(dto: ProjectResponseDto): Implementation {
  return {
    id: dto.id,
    projectType: dto.roadmap_project,
    language: canonicalLanguage(dto.programming_language),
    githubUrl: dto.github_repository_url,
    submittedAt: new Date(dto.added_timestamp * 1000),
  }
}

// One form per repository, so a trailing "/" or ".git" doesn't get past project-service's
// duplicate check (409) as a different link. Case is kept as typed.
export function canonicalGithubUrl(url: string) {
  return url.trim().replace(/\/+$/, '').replace(/\.git$/i, '')
}
