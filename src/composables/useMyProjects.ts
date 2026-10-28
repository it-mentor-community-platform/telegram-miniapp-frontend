import { readonly, ref } from 'vue'
import { ApiError, getMyProjectsSummary } from '../api'
import { toLanguagesByProjectType, type LanguagesByProjectType } from '../roadmap'

// Shared by home and the projects page, so moving between them shows the last data at once while
// a fresh copy loads.
const languagesByType = ref<LanguagesByProjectType>()
const loading = ref(false)
const failed = ref(false)

let request: Promise<void> | undefined

// The current student's languages per project type. Call load() whenever a screen opens.
export function useMyProjects() {
  return {
    languagesByType: readonly(languagesByType),
    loading: readonly(loading),
    failed: readonly(failed),
    load,
  }
}

function load() {
  request ??= fetchSummary().finally(() => (request = undefined))
  return request
}

async function fetchSummary() {
  loading.value = true
  try {
    languagesByType.value = toLanguagesByProjectType(await getMyProjectsSummary())
    failed.value = false
  } catch (error) {
    // A 401 also lands here, but the app shell already shows the expired screen for it.
    if (!(error instanceof ApiError)) {
      console.error('Unexpected projects summary error', error)
    }
    failed.value = true
  } finally {
    loading.value = false
  }
}
