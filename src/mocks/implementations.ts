// Mocked implementations until project-service can list them. Each project type has a fixed
// scenario for UI testing; submissions are kept in memory until reload.
//
// Test triggers: a repository named "fail" makes the submit fail; `?mock=load-error` in the page
// URL makes loading fail; `?mock=slow` slows every request down to 3 s.

import type { ProjectTypeId } from '../roadmap'

export type Implementation = {
  id: number
  projectType: ProjectTypeId
  language: string
  githubUrl: string
  deployUrl?: string
  submittedAt: Date
}

export type NewImplementation = Pick<Implementation, 'projectType' | 'language' | 'githubUrl' | 'deployUrl'>

// The repository is already registered as an implementation (the backend's 409).
export class DuplicateRepositoryError extends Error {}

export class MockRequestError extends Error {}

const seed: Omit<Implementation, 'id'>[] = [
  // HANGMAN, TENNIS_SCOREBOARD: nothing submitted.
  { projectType: 'SIMULATION', language: 'Java', githubUrl: 'https://github.com/sergey-dev/simulation', submittedAt: new Date('2025-11-20') },
  { projectType: 'CURRENCY_EXCHANGE', language: 'Python', githubUrl: 'https://github.com/sergey-dev/currency-exchange-fastapi', deployUrl: 'https://currency-py.sergey-dev.ru', submittedAt: new Date('2026-05-05') },
  { projectType: 'CURRENCY_EXCHANGE', language: 'Java', githubUrl: 'https://github.com/sergey-dev/currency-exchange-spring', deployUrl: 'https://currency.sergey-dev.ru', submittedAt: new Date('2026-03-12') },
  { projectType: 'CURRENCY_EXCHANGE', language: 'Java', githubUrl: 'https://github.com/sergey-dev/currency-exchange', submittedAt: new Date('2026-01-18') },
  { projectType: 'CLOUD_FILE_STORAGE', language: 'Kotlin', githubUrl: 'https://github.com/sergey-dev/cloud-storage-ktor', deployUrl: 'https://cloud.sergey-dev.ru', submittedAt: new Date('2026-06-02') },
  { projectType: 'CLOUD_FILE_STORAGE', language: 'Rust', githubUrl: 'https://github.com/sergey-dev/cloud-storage-rs', submittedAt: new Date('2026-04-14') },
  { projectType: 'TASK_TRACKER', language: 'Go', githubUrl: 'https://github.com/sergey-dev/task-tracker-go', deployUrl: 'https://tasks-go.sergey-dev.ru', submittedAt: new Date('2026-09-30') },
  { projectType: 'TASK_TRACKER', language: 'Python', githubUrl: 'https://github.com/sergey-dev/task-tracker-django', submittedAt: new Date('2026-08-11') },
  { projectType: 'TASK_TRACKER', language: 'Java', githubUrl: 'https://github.com/sergey-dev/task-tracker', deployUrl: 'https://tasks.sergey-dev.ru', submittedAt: new Date('2026-07-01') },
]

const store: Implementation[] = seed.map((implementation, index) => ({ ...implementation, id: index + 1 }))

const trigger = new URLSearchParams(window.location.search).get('mock')

// Newest first.
export async function getMyImplementations(projectType: ProjectTypeId): Promise<Implementation[]> {
  await delay()
  if (trigger === 'load-error') {
    throw new MockRequestError('Mocked load error')
  }
  return store
    .filter((implementation) => implementation.projectType === projectType)
    .sort((a, b) => b.submittedAt.getTime() - a.submittedAt.getTime())
}

export async function submitImplementation(input: NewImplementation): Promise<Implementation> {
  await delay()
  const repository = canonicalRepository(input.githubUrl)
  if (repository.endsWith('/fail')) {
    throw new MockRequestError('Mocked submit error')
  }
  if (store.some((implementation) => canonicalRepository(implementation.githubUrl) === repository)) {
    throw new DuplicateRepositoryError(repository)
  }
  const implementation = { ...input, id: store.length + 1, submittedAt: new Date() }
  store.push(implementation)
  return implementation
}

// An implementation is identified by its repository: "github.com/owner/repo", case-insensitive.
function canonicalRepository(url: string) {
  return url
    .trim()
    .toLowerCase()
    .replace(/^https?:\/\/(www\.)?/, '')
    .replace(/\/$/, '')
    .replace(/\.git$/, '')
}

function delay() {
  return new Promise((resolve) => setTimeout(resolve, trigger === 'slow' ? 3000 : 600))
}
