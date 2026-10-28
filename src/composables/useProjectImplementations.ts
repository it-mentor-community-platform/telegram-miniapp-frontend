import { readonly, ref } from 'vue'
import {
  getMyImplementations,
  submitImplementation,
  type Implementation,
  type NewImplementation,
} from '../mocks/implementations'
import type { ProjectTypeId } from '../roadmap'

// The current student's implementations of one project type, for the project page.
export function useProjectImplementations(projectType: ProjectTypeId) {
  const implementations = ref<Implementation[]>()
  const loading = ref(false)
  const failed = ref(false)

  async function load() {
    loading.value = true
    try {
      implementations.value = await getMyImplementations(projectType)
      failed.value = false
    } catch {
      failed.value = true
    } finally {
      loading.value = false
    }
  }

  // Rejects with the submit error for the form to show. If the list failed to load, it stays
  // failed: showing only the new implementation would look like the full list.
  async function submit(input: Omit<NewImplementation, 'projectType'>) {
    const implementation = await submitImplementation({ ...input, projectType })
    if (implementations.value) {
      implementations.value = [implementation, ...implementations.value]
    }
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
