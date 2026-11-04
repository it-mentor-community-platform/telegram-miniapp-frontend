import { readonly, ref } from 'vue'
import { ApiError, getMyProject, NotFoundError, updateMyProject } from '../api'
import { canonicalGithubUrl, toImplementation, type Implementation } from '../roadmap'

export type ImplementationChange = {
  githubUrl?: string
  // null removes the deploy link.
  deployUrl?: string | null
}

// One implementation of the current student, for the implementation page.
export function useImplementation(id: number) {
  const implementation = ref<Implementation>()
  const loading = ref(false)
  const failed = ref(false)
  const notFound = ref(false)

  async function load() {
    loading.value = true
    try {
      implementation.value = toImplementation(await getMyProject(id))
      failed.value = false
    } catch (error) {
      if (error instanceof NotFoundError) {
        notFound.value = true
      } else {
        // A 401 also lands here, but the app shell already shows the expired screen for it.
        if (!(error instanceof ApiError)) {
          console.error('Unexpected implementation error', error)
        }
        failed.value = true
      }
    } finally {
      loading.value = false
    }
  }

  // Rejects with the save error for the card to show (ConflictError for a repository in use).
  // Type and language can't change, so the cached progress summary stays valid.
  async function update(change: ImplementationChange) {
    const current = implementation.value!
    implementation.value = toImplementation(
      await updateMyProject(id, {
        github_repository_url: canonicalGithubUrl(change.githubUrl ?? current.githubUrl),
        ...(change.deployUrl !== undefined && { deployment_url: change.deployUrl?.trim() ?? null }),
      }),
    )
  }

  return {
    implementation: readonly(implementation),
    loading: readonly(loading),
    failed: readonly(failed),
    notFound: readonly(notFound),
    load,
    update,
  }
}
