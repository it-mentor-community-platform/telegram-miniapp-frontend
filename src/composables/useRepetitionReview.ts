import { computed, onScopeDispose, readonly, ref, shallowRef, watch, type Ref } from 'vue'
import {
  getNextQuestionFromCategory, getNextQuestionFromSelectedCategories, submitReviewAttempt,
  HttpError, NotFoundError, type NextQuestionResponseDto, type ReviewQuality,
} from '../api'
import { session } from '../session'
import { REVIEW_RATINGS } from '../repetition'
import { useRepetitionTopics } from './useRepetitionTopics'

export type ReviewScope = { valid: true; topicId?: number } | { valid: false }
export type ReviewPhase = 'loading' | 'question' | 'saving' | 'load-error' | 'save-error' | 'uncertain' | 'done' | 'not-found'

export function useRepetitionReview(scope: Readonly<Ref<ReviewScope>>) {
  const question = ref<NextQuestionResponseDto>()
  const revealed = ref(false)
  const phase = ref<ReviewPhase>('loading')
  const error = shallowRef<unknown>()
  const answers = ref<{ questionId: number; categoryId: number; quality: ReviewQuality }[]>([])
  const unconfirmed = ref(0)
  const remaining = ref(0)
  let generation = 0
  let busy = false
  let uncertainQuestionId: number | undefined
  const { refresh: refreshCatalog } = useRepetitionTopics()

  const completed = computed(() => answers.value.length + unconfirmed.value)
  const total = computed(() => completed.value + remaining.value)
  const progress = computed(() => phase.value === 'done' ? 100 : total.value ? Math.round(completed.value / total.value * 100) : 0)
  const summary = computed(() => REVIEW_RATINGS.map((rating) => ({
    ...rating,
    count: answers.value.filter((answer) => answer.quality === rating.quality).length,
  })))
  const topicCount = computed(() => new Set(answers.value.map((answer) => answer.categoryId)).size)

  async function fetchNext(currentGeneration: number) {
    const currentScope = scope.value
    if (!currentScope.valid) return
    const next = currentScope.topicId === undefined
      ? await getNextQuestionFromSelectedCategories()
      : await getNextQuestionFromCategory(currentScope.topicId)
    if (currentGeneration !== generation) return
    if (uncertainQuestionId !== undefined) {
      // A failed non-idempotent POST must not be sent again automatically. If the server still
      // offers the same question, keep it blocked; the user can check again or leave the session.
      if (next?.questionId === uncertainQuestionId) {
        question.value = next
        remaining.value = next.questions_left + 1
        phase.value = 'uncertain'
        return
      }
      // Queue movement does not prove the lost POST succeeded (another tab may have answered).
      unconfirmed.value++
      uncertainQuestionId = undefined
    }
    question.value = next ?? undefined
    remaining.value = next ? next.questions_left + 1 : 0
    revealed.value = false
    error.value = undefined
    phase.value = next ? 'question' : 'done'
    if (!next) void refreshCatalog()
  }

  // Retrying a GET never resubmits a confirmed or uncertain assessment.
  async function loadNext() {
    if (busy || !scope.value.valid) return
    busy = true
    const currentGeneration = generation
    phase.value = 'loading'
    error.value = undefined
    try {
      await fetchNext(currentGeneration)
    } catch (cause) {
      if (currentGeneration !== generation) return
      error.value = cause
      phase.value = cause instanceof NotFoundError ? 'not-found' : 'load-error'
    } finally {
      if (currentGeneration === generation) busy = false
    }
  }

  function reveal() {
    if (phase.value === 'question') revealed.value = true
  }

  function hide() {
    if (phase.value === 'question') revealed.value = false
  }

  async function rate(quality: ReviewQuality) {
    if (busy || !question.value || !['question', 'save-error'].includes(phase.value)) return
    if (!REVIEW_RATINGS.some((rating) => rating.quality === quality)) return
    busy = true
    const currentGeneration = generation
    const currentQuestion = question.value
    phase.value = 'saving'
    error.value = undefined
    try {
      await submitReviewAttempt({ questionId: currentQuestion.questionId, quality })
    } catch (cause) {
      if (currentGeneration !== generation) return
      error.value = cause
      if (cause instanceof HttpError && cause.status >= 400 && cause.status < 500) {
        phase.value = 'save-error'
      } else {
        uncertainQuestionId = currentQuestion.questionId
        phase.value = 'uncertain'
      }
      busy = false
      return
    }
    if (currentGeneration !== generation) return
    answers.value.push({ questionId: currentQuestion.questionId, categoryId: currentQuestion.categoryId, quality })
    remaining.value = Math.max(0, remaining.value - 1)
    // Keep the current content in place during the next GET. Controls are locked by phase;
    // fetchNext replaces it and resets answer visibility once the next question arrives.
    void refreshCatalog()
    try {
      phase.value = 'loading'
      await fetchNext(currentGeneration)
    } catch (cause) {
      if (currentGeneration !== generation) return
      error.value = cause
      phase.value = cause instanceof NotFoundError ? 'not-found' : 'load-error'
    } finally {
      if (currentGeneration === generation) busy = false
    }
  }

  watch([scope, () => session.status === 'authenticated' ? session.user?.telegramUserId : undefined], () => {
    generation++
    busy = false
    question.value = undefined
    revealed.value = false
    error.value = undefined
    answers.value = []
    unconfirmed.value = 0
    remaining.value = 0
    uncertainQuestionId = undefined
    phase.value = scope.value.valid ? 'loading' : 'not-found'
    if (scope.value.valid && session.status === 'authenticated') void loadNext()
  }, { immediate: true, flush: 'sync' })
  onScopeDispose(() => { generation++ })

  return {
    question: readonly(question), revealed: readonly(revealed), phase: readonly(phase), error: readonly(error),
    answers: readonly(answers), unconfirmed: readonly(unconfirmed), remaining: readonly(remaining), completed, total, progress, summary, topicCount,
    reveal, hide, rate, loadNext,
  }
}
