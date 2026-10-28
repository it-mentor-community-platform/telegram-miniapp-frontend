// Roadmap project keys of project-service (`RoadmapProject`). The summary uses the enum names, with
// underscores, not the hyphenated values the enum accepts elsewhere.
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
