// The service has no learned-question metric yet. Kept separate from real API counters.
// A neutral placeholder until statistics are available; not calculated from scheduled questions.
export function getTopicLearnedPercent(): number {
  return 0
}

// Per-question progress and review dates are not exposed by the service yet.
export function getQuestionStatus(): string {
  return 'Статус недоступен'
}
