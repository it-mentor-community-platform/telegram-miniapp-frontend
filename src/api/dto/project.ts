// Roadmap project keys of project-service (`RoadmapProject`), as it sends them: enum names, with
// underscores. It also accepts the hyphenated form, but we always send these.
export type RoadmapProjectDto =
  | 'HANGMAN'
  | 'SIMULATION'
  | 'CURRENCY_EXCHANGE'
  | 'TENNIS_SCOREBOARD'
  | 'WEATHER_VIEWER'
  | 'CLOUD_FILE_STORAGE'
  | 'TASK_TRACKER'
  | 'OTHER'

// Response of GET /api/project/projects/my/summary: languages of the current student's
// implementations per roadmap project. Projects without implementations are absent.
export type ProjectsSummaryDto = Partial<Record<RoadmapProjectDto, string[]>>

// One implementation (`ProjectResponse`): an item of GET /api/project/projects/my and the body of
// POST /api/project/project. The spec's POST 201 schema is a camelCase `Project`, but its example
// is this snake_case shape, as is the GET response; we follow the example.
export type ProjectResponseDto = {
  id: number
  author_telegram_user_id: number
  github_repository_url: string
  programming_language: string
  roadmap_project: RoadmapProjectDto
  // Epoch seconds.
  added_timestamp: number
  // Only for project types with a deploy; null when not set. In the system analytics spec, not yet
  // in project-service's OpenAPI (absent from its responses so far).
  deployment_url?: string | null
}

// Body of POST /api/project/project, required fields only (the optional `added_timestamp` and
// `project_source_type` are not sent). The author comes from the access token: the gateway adds
// the user headers.
export type CreateProjectRequestDto = {
  github_repository_url: string
  programming_language: string
  roadmap_project: RoadmapProjectDto
}

// Body of PATCH /api/project/projects/{id} (system analytics spec, not yet in OpenAPI). The GitHub
// URL is always sent: a body without it is a 400. `deployment_url`: omitted - unchanged, null -
// removed.
export type UpdateProjectRequestDto = {
  github_repository_url: string
  deployment_url?: string | null
}
