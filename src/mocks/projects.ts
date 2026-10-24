// Mocked project implementations until project-service exposes a read endpoint.
// Pick a scenario with VITE_MOCK_PROJECTS: empty | java3 | multi | java6 | other (default multi).

import type { LanguagesByProjectType } from '../roadmap'

type Scenario = 'empty' | 'java3' | 'multi' | 'java6' | 'other'

const scenarios: Record<Scenario, LanguagesByProjectType> = {
  empty: languages([], [], [], [], [], []),
  java3: languages(['Java'], [], ['Java'], ['Java'], [], []),
  multi: languages(['Java', 'Python', 'Go'], ['Java', 'C#'], ['Java', 'Python'], [], [], []),
  java6: languages(['Java'], ['Java'], ['Java'], ['Java'], ['Java'], ['Java']),
  other: languages(['C#'], [], ['Rust'], [], [], []),
}

export function getMyProjects(): LanguagesByProjectType {
  const scenario = (import.meta.env.VITE_MOCK_PROJECTS ?? 'multi') as Scenario
  return scenarios[scenario] ?? scenarios.multi
}

function languages(...byType: string[][]): LanguagesByProjectType {
  const [hangman, simulation, exchange, tennis, cloud, scheduler] = byType
  return {
    hangman,
    simulation,
    'currency-exchange': exchange,
    'tennis-scoreboard': tennis,
    'cloud-storage': cloud,
    'task-scheduler': scheduler,
  }
}
