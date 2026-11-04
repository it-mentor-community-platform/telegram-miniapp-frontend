// Mocked GET/PATCH /api/project/projects/{id} until project-service ships them (system analytics:
// meta/system-analytics/services/project-service/index.md). Replace the bodies of getMyProject() and
// updateMyProject() in src/api/projects.ts with real requests; screens should not need to change.
//
// - Demo implementations (ids from 900001, the mockups' data) cover each design state.
// - Any other id is looked up in the student's real implementations (GET /projects/my).
// - Edits are kept in memory only: a reload brings back the stored links.
// - In test environments, `?mock=<scenario>` in the page URL forces a corner case (MOCK_SCENARIOS).

import type { ProjectResponseDto, UpdateProjectRequestDto } from '../api/dto/project'
import { BadRequestError, ConflictError, NotFoundError, ServerError } from '../api/errors'
import { getMyProjectImplementations } from '../api/projects'
import { canonicalGithubUrl, isGithubRepositoryUrl, isHttpsUrl, PROJECT_TYPES } from '../roadmap'

export const MOCK_SCENARIOS = {
  loading: 'Загрузка не заканчивается',
  'load-error': 'Ошибка загрузки (500)',
  'not-found': 'Не найдена (404)',
  'save-conflict': 'Сохранение: ссылка занята (409)',
  'save-error': 'Сохранение: ошибка сервера (500)',
} as const

type MockScenario = keyof typeof MOCK_SCENARIOS

const LATENCY_MS = 600

// Seconds since the epoch, for a calendar day.
const day = (iso: string) => Date.parse(`${iso}T12:00:00Z`) / 1000

export const DEMO_IMPLEMENTATIONS: (ProjectResponseDto & { title: string })[] = [
  {
    title: 'Обмен валют · Java — деплой',
    id: 900001,
    author_telegram_user_id: 0,
    github_repository_url: 'https://github.com/sergey-dev/currency-exchange-spring',
    programming_language: 'Java',
    roadmap_project: 'CURRENCY_EXCHANGE',
    added_timestamp: day('2026-03-12'),
    deployment_url: 'https://currency.sergey-dev.ru',
  },
  {
    title: 'Виселица · Java — без деплоя',
    id: 900002,
    author_telegram_user_id: 0,
    github_repository_url: 'https://github.com/sergey-dev/hangman',
    programming_language: 'Java',
    roadmap_project: 'HANGMAN',
    added_timestamp: day('2025-11-02'),
    deployment_url: null,
  },
  {
    title: 'Обмен валют · Java — ссылка на деплой не указана',
    id: 900003,
    author_telegram_user_id: 0,
    github_repository_url: 'https://github.com/sergey-dev/currency-exchange',
    programming_language: 'Java',
    roadmap_project: 'CURRENCY_EXCHANGE',
    added_timestamp: day('2026-01-18'),
    deployment_url: null,
  },
  {
    title: 'Обмен валют · Python',
    id: 900004,
    author_telegram_user_id: 0,
    github_repository_url: 'https://github.com/sergey-dev/currency-exchange-fastapi',
    programming_language: 'Python',
    roadmap_project: 'CURRENCY_EXCHANGE',
    added_timestamp: day('2026-05-05'),
    deployment_url: 'https://currency-py.sergey-dev.ru',
  },
  {
    title: 'Обмен валют · Kotlin — вне роадмапов',
    id: 900005,
    author_telegram_user_id: 0,
    github_repository_url: 'https://github.com/sergey-dev/currency-exchange-ktor',
    programming_language: 'Kotlin',
    roadmap_project: 'CURRENCY_EXCHANGE',
    added_timestamp: day('2026-06-20'),
    deployment_url: null,
  },
]

// A repository URL another implementation already uses: saving it is a 409.
export const TAKEN_GITHUB_URL = DEMO_IMPLEMENTATIONS[3].github_repository_url

// Current state of every implementation the mock has served, with edits applied.
const known = new Map<number, ProjectResponseDto>(
  DEMO_IMPLEMENTATIONS.map(({ title: _title, ...implementation }) => [implementation.id, implementation]),
)
const edited = new Set<number>()

function scenario(): MockScenario | undefined {
  if (import.meta.env.VITE_SHOW_DEV_TOOLS !== 'true') {
    return undefined
  }
  const value = new URLSearchParams(window.location.search).get('mock')
  return value && value in MOCK_SCENARIOS ? (value as MockScenario) : undefined
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const errorBody = (message: string) => ({ message })

// The real implementations, fetched for each roadmap project type. Edited ones keep their edits.
async function loadReal() {
  const lists = await Promise.all(PROJECT_TYPES.map((type) => getMyProjectImplementations(type.id)))
  for (const implementation of lists.flat()) {
    if (!edited.has(implementation.id)) {
      known.set(implementation.id, { deployment_url: null, ...implementation })
    }
  }
}

export async function mockGetProject(id: number): Promise<ProjectResponseDto> {
  const forced = scenario()
  if (forced === 'loading') {
    return new Promise(() => {})
  }
  await delay(LATENCY_MS)
  if (forced === 'load-error') {
    throw new ServerError(500, errorBody('Mocked server error'))
  }
  if (forced === 'not-found') {
    throw new NotFoundError(404, errorBody('Mocked: project not found'))
  }
  // Real ids: fresh from the backend, unless edited here.
  const demo = DEMO_IMPLEMENTATIONS.some((implementation) => implementation.id === id)
  if (!demo && !edited.has(id)) {
    await loadReal()
  }
  const implementation = known.get(id)
  if (!implementation) {
    throw new NotFoundError(404, errorBody('Project not found'))
  }
  return { ...implementation }
}

export async function mockUpdateProject(id: number, request: UpdateProjectRequestDto): Promise<ProjectResponseDto> {
  await delay(LATENCY_MS)
  const forced = scenario()
  if (forced === 'save-error') {
    throw new ServerError(500, errorBody('Mocked server error'))
  }
  if (forced === 'save-conflict') {
    throw new ConflictError(409, errorBody('Mocked: repository already registered'))
  }

  const current = known.get(id)
  if (!current) {
    throw new NotFoundError(404, errorBody('Project not found'))
  }

  // The spec's validation, so the mock rejects what the backend would.
  const github = request.github_repository_url
  if (!github || !isGithubRepositoryUrl(github)) {
    throw new BadRequestError(400, errorBody('Invalid github_repository_url'))
  }
  const deployable = PROJECT_TYPES.find((type) => type.id === current.roadmap_project)?.deployable ?? false
  const deploy = request.deployment_url
  if (deploy === '' || (deploy && !isHttpsUrl(deploy)) || (deploy && !deployable)) {
    throw new BadRequestError(400, errorBody('Invalid deployment_url'))
  }

  // Unique among the other implementations; the implementation's own URL is a no-op change.
  const key = canonicalGithubUrl(github).toLowerCase()
  const taken = [...known.values()].some(
    (other) => other.id !== id && canonicalGithubUrl(other.github_repository_url).toLowerCase() === key,
  )
  if (taken) {
    throw new ConflictError(409, errorBody('Project with this repository already exists'))
  }

  const updated: ProjectResponseDto = {
    ...current,
    github_repository_url: github,
    ...(deploy !== undefined && { deployment_url: deploy }),
  }
  known.set(id, updated)
  edited.add(id)
  return { ...updated }
}
