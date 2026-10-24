// Roadmap facts shared by screens: the fixed project types and the languages that count toward
// progress (see meta/business-analytics/functionality/student-roadmap-completion.md).

export type ProjectTypeSlug =
  | 'hangman'
  | 'simulation'
  | 'currency-exchange'
  | 'tennis-scoreboard'
  | 'cloud-storage'
  | 'task-scheduler'

export type ProjectIcon = 'hangman' | 'simulation' | 'exchange' | 'tennis' | 'cloud' | 'planner'

export type ProjectType = {
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
export type LanguagesByProjectType = Record<ProjectTypeSlug, string[]>

// In roadmap order.
export const PROJECT_TYPES: ProjectType[] = [
  { slug: 'hangman', title: 'Виселица', icon: 'hangman' },
  { slug: 'simulation', title: 'Симуляция', icon: 'simulation' },
  { slug: 'currency-exchange', title: 'Обмен валют', icon: 'exchange' },
  { slug: 'tennis-scoreboard', title: 'Теннисное табло', icon: 'tennis' },
  { slug: 'cloud-storage', title: 'Облачное хранилище', icon: 'cloud' },
  { slug: 'task-scheduler', title: 'Планировщик задач', icon: 'planner' },
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
    steps: PROJECT_TYPES.map((type) => languagesByType[type.slug].includes(language)),
  })).filter((track) => track.steps.some(Boolean))
}
