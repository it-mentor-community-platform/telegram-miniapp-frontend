import { readonly, ref } from 'vue'
import { ApiError, createProject, getMyProjectImplementations } from '../api'
import {
  canonicalGithubUrl,
  toImplementation,
  type Implementation,
  type NewImplementation,
  type ProjectTypeId,
} from '../roadmap'
import { useMyProjects } from './useMyProjects'

// The current student's implementations of one project type, for the project page.
export function useProjectImplementations(projectType: ProjectTypeId) {
  const implementations = ref<Implementation[]>()
  const loading = ref(false)
  const failed = ref(false)

  async function load() {
    loading.value = true
    try {
      // Already newest first.
      implementations.value = (await getMyProjectImplementations(projectType)).map(toImplementation)
      failed.value = false
    } catch (error) {
      // A 401 also lands here, but the app shell already shows the expired screen for it.
      if (!(error instanceof ApiError)) {
        console.error('Unexpected project implementations error', error)
      }
      failed.value = true
    } finally {
      loading.value = false
    }
  }

  // Rejects with the submit error for the form to show (ConflictError for a duplicate repository).
  // If the list failed to load, it stays failed: showing only the new implementation would look
  // like the full list.
  async function submit(input: NewImplementation) {
    const implementation = toImplementation(
      await createProject({
        github_repository_url: canonicalGithubUrl(input.githubUrl),
        programming_language: input.language,
        roadmap_project: projectType,
      }),
    )
    if (implementations.value) {
      implementations.value = [implementation, ...implementations.value]
    }
    // The cached summary behind home and the projects screen is now stale; refresh it in the
    // background.
    void useMyProjects().load()
    return implementation
  }

  return {
    implementations: readonly(implementations),
    loading: readonly(loading),
    failed: readonly(failed),
    load,
    submit,
  }
}
