// Mocked homepage data until the backend exposes repetition stats and achievements.
// Replace getHomeData() with API calls; screens should not need to change.

export type StatTone = 'warn' | 'info' | 'success' | 'neutral'

export type StatItem = {
  value: string | number
  label: string
  tone: StatTone
}

export type HomeData = {
  repetitionStats: StatItem[]
  achievementCount: number
}

export function getHomeData(): HomeData {
  return {
    repetitionStats: [
      { value: 12, label: 'к повторению', tone: 'warn' },
      { value: 5, label: 'тем', tone: 'neutral' },
      { value: 108, label: 'выучено', tone: 'neutral' },
    ],
    achievementCount: 4,
  }
}
