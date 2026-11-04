import { computed, readonly, ref, shallowRef, watch } from 'vue'
import {
  deleteSelectedCategory,
  getSpecializations,
  saveSelectedCategories,
  type SelectedCategoryResponseDto,
  type SpecializationResponseDto,
} from '../api'
import { session } from '../session'

// One catalog is the source of truth for both catalog and selected-topic screens.
// undefined means not loaded; [] means a successfully loaded empty catalog.
const specializations = ref<SpecializationResponseDto[]>()
const loading = ref(false)
const loadError = shallowRef<unknown>()
const pendingIds = ref<Set<number>>(new Set())
const actionErrors = shallowRef<ReadonlyMap<number, unknown>>(new Map())

let loadRequest: Promise<void> | undefined
const actions = new Map<number, Promise<void>>()
let generation = 0
let revision = 0

const selectedCategories = computed<SelectedCategoryResponseDto[] | undefined>(() =>
  specializations.value?.flatMap((specialization) =>
    specialization.categories.filter((category) => category.selected).map((category) => ({
      id: category.id,
      name: category.name,
      specialization: specialization.name,
      new_questions: category.new_questions,
      questions_ready_to_repeat: category.questions_ready_to_repeat,
      all_questions: category.all_questions,
    })),
  ),
)

// Clear cached personal data and ignore late responses after logout or a different login.
watch(
  () => session.status === 'authenticated' ? session.user?.telegramUserId : undefined,
  reset,
  { flush: 'sync' },
)

function reset() {
  generation++
  revision++
  specializations.value = undefined
  loading.value = false
  loadError.value = undefined
  pendingIds.value = new Set()
  actionErrors.value = new Map()
  loadRequest = undefined
  actions.clear()
}

// Call on screen entry or after a review session. Concurrent callers share one request.
// Errors are exposed as state; existing data stays visible while refreshing or on failure.
function load(): Promise<void> {
  if (loadRequest) return loadRequest
  const currentGeneration = generation
  loading.value = true
  loadError.value = undefined
  const request = (async () => {
    try {
      // A selection may change during a fetch. Refetch instead of applying a stale snapshot.
      let fetchedRevision: number
      let data: SpecializationResponseDto[]
      do {
        fetchedRevision = revision
        data = await getSpecializations()
        if (currentGeneration !== generation) return
      } while (fetchedRevision !== revision)
      specializations.value = data
    } catch (error) {
      if (currentGeneration === generation) loadError.value = error
    } finally {
      if (currentGeneration === generation) {
        loading.value = false
        loadRequest = undefined
      }
    }
  })()
  loadRequest = request
  return request
}

// Update only after the server confirms. Repeated clicks on the same topic share its action;
// other topics remain interactive. Errors are stored per topic and consumed by the screen.
function setSelected(categoryId: number, selected: boolean): Promise<void> {
  const existing = actions.get(categoryId)
  if (existing) return existing
  const currentGeneration = generation
  pendingIds.value.add(categoryId)
  const errors = new Map(actionErrors.value)
  errors.delete(categoryId)
  actionErrors.value = errors

  const request = (async () => {
    try {
      if (selected) {
        await saveSelectedCategories({ categoryIds: [categoryId] })
      } else {
        await deleteSelectedCategory(categoryId)
      }
      if (currentGeneration !== generation) return
      revision++
      for (const specialization of specializations.value ?? []) {
        const category = specialization.categories.find((item) => item.id === categoryId)
        if (category) category.selected = selected
      }
    } catch (error) {
      if (currentGeneration === generation) {
        actionErrors.value = new Map(actionErrors.value).set(categoryId, error)
      }
    } finally {
      if (currentGeneration === generation) {
        pendingIds.value.delete(categoryId)
        actions.delete(categoryId)
      }
    }
  })()
  actions.set(categoryId, request)
  return request
}

export function useRepetitionTopics() {
  return {
    specializations: readonly(specializations),
    selectedCategories: readonly(selectedCategories),
    loading: readonly(loading),
    loadError: readonly(loadError),
    pendingIds: readonly(pendingIds),
    actionErrors: readonly(actionErrors),
    load,
    setSelected,
  }
}
