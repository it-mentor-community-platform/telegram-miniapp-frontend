import { onScopeDispose, readonly, ref, shallowRef, watch, type Ref } from 'vue'
import { getCategoryWithQuestions, NotFoundError, type CategoryWithQuestionsResponseDto } from '../api'
import { session } from '../session'

// Page-local detail data. Ignore late responses after changing the route, session, or leaving.
export function useRepetitionTopic(topicId: Readonly<Ref<number | undefined>>) {
  const topic = ref<CategoryWithQuestionsResponseDto>()
  const loading = ref(false)
  const error = shallowRef<unknown>()
  const notFound = ref(false)
  let requestId = 0

  async function load() {
    const id = topicId.value
    const currentRequest = ++requestId
    error.value = undefined
    notFound.value = id === undefined
    if (id === undefined) {
      topic.value = undefined
      loading.value = false
      return
    }
    loading.value = true
    try {
      const data = await getCategoryWithQuestions(id)
      if (currentRequest === requestId) topic.value = data
    } catch (cause) {
      if (currentRequest !== requestId) return
      if (cause instanceof NotFoundError) {
        topic.value = undefined
        notFound.value = true
      } else {
        error.value = cause
      }
    } finally {
      if (currentRequest === requestId) loading.value = false
    }
  }

  watch(
    [topicId, () => session.status === 'authenticated' ? session.user?.telegramUserId : undefined],
    () => {
      ++requestId
      topic.value = undefined
      error.value = undefined
      loading.value = false
      notFound.value = topicId.value === undefined
      if (session.status === 'authenticated') void load()
    },
    { immediate: true, flush: 'sync' },
  )
  onScopeDispose(() => { ++requestId })

  return { topic: readonly(topic), loading: readonly(loading), error: readonly(error), notFound: readonly(notFound), load }
}
