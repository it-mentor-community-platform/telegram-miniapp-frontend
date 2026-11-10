import type { ReviewQuality } from './api/dto/interval-repetition'

// Product mapping: the first two choices fail SM-2 (<3), the other two succeed.
export const REVIEW_RATINGS: { label: string; quality: ReviewQuality }[] = [
  { label: 'Не помню', quality: 0 },
  { label: 'Отрывочно', quality: 2 },
  { label: 'С пробелами', quality: 3 },
  { label: 'Отлично', quality: 5 },
]
