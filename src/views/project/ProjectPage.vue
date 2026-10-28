<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'
import ListSection from '../../components/ListSection.vue'
import { useProjectImplementations } from '../../composables/useProjectImplementations'
import type { Implementation } from '../../mocks/implementations'
import { isTracked, joinRussian, PROJECT_TYPES, sortLanguages, specLinks, type ProjectType } from '../../roadmap'
import ImplementationForm from './ImplementationForm.vue'
import ImplementationRow from './ImplementationRow.vue'

// One roadmap project of the current student; see design/ProjectType.dc.html and
// README → "Project page data".
const props = defineProps<{
  projectType: ProjectType
}>()

const { implementations, loading, failed, load, submit } = useProjectImplementations(props.projectType.id)
load()

const position = PROJECT_TYPES.indexOf(props.projectType) + 1
const specs = specLinks(props.projectType)

// 'failed' only once loading has stopped, so a retry shows the skeleton again.
const loadState = computed(() =>
  implementations.value ? 'loaded' : failed.value && !loading.value ? 'failed' : 'loading',
)
const languages = computed(() => sortLanguages((implementations.value ?? []).map((item) => item.language)))
const submitted = computed(() => languages.value.length > 0)

const formOpen = ref(false)
const formEdited = ref(false)
const success = ref<{ title: string; text: string }>()
const highlightedId = ref<number>()

// Nothing known to be submitted (still loading, none yet, or the list failed to load): the form is
// simply open. Otherwise it opens from «Добавить реализацию».
const showForm = computed(() => {
  if (success.value) {
    return formOpen.value
  }
  return !submitted.value || formOpen.value
})

// A list that arrives non-empty collapses the form, unless the user has started filling it in.
watch(loadState, (state) => {
  if (state === 'loaded' && submitted.value && formEdited.value) {
    formOpen.value = true
  }
})

function openForm() {
  success.value = undefined
  formOpen.value = true
}

function closeForm() {
  formOpen.value = false
  formEdited.value = false
}

function onSubmitted(implementation: Implementation) {
  closeForm()
  success.value = {
    title: implementations.value?.length === 1 ? 'Проект сдан' : 'Реализация добавлена',
    text: isTracked(implementation.language)
      ? `Реализация на ${implementation.language} засчитана в прогресс ${implementation.language} Backend.`
      : 'Реализация сохранена. В прогресс роадмапов она не попадает.',
  }
  // The new row is tinted, then fades back (the row's transition) after a moment.
  highlightedId.value = implementation.id
  setTimeout(() => (highlightedId.value = undefined), 2000)
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <header class="flex flex-col gap-1.5">
      <h1 class="text-2xl/[1.875rem] font-bold">{{ projectType.title }}</h1>
      <p class="flex min-h-4.5 flex-wrap items-center gap-2 text-meta">
        <span class="font-medium text-muted-color">Проект {{ position }} из {{ PROJECT_TYPES.length }}</span>
        <template v-if="loadState !== 'failed'">
          <span class="text-subtle-color" aria-hidden="true">·</span>
          <Skeleton v-if="loadState === 'loading'" width="7.5rem" height="0.875rem" />
          <span v-else-if="submitted" class="inline-flex items-center gap-1 font-semibold text-primary">
            <i class="pi pi-check text-xs" aria-hidden="true" />Сдан на {{ joinRussian(languages) }}
          </span>
          <span v-else class="font-medium text-muted-color">Ещё не сдан</span>
        </template>
      </p>
    </header>

    <section class="flex flex-col gap-2" aria-labelledby="project-spec">
      <h2 id="project-spec" class="px-1 text-meta font-semibold tracking-[0.04em] text-muted-color uppercase">
        Техническое задание
      </h2>
      <div class="grid grid-cols-3 gap-2">
        <Button
          v-for="spec in specs"
          :key="spec.language"
          as="a"
          :href="spec.url"
          target="_blank"
          rel="noopener"
          :label="spec.language"
          icon="pi pi-external-link"
          icon-pos="right"
          severity="secondary"
          variant="outlined"
          class="bg-(--p-content-background) text-color hover:bg-emphasis"
          :pt="{ icon: { class: 'text-xs text-muted-color' } }"
        />
      </div>
    </section>

    <Message v-if="success" severity="success" closable role="status" @close="success = undefined">
      <span class="flex flex-col gap-0.5">
        <span class="font-bold">{{ success.title }}</span>
        <span class="text-meta text-color">{{ success.text }}</span>
      </span>
    </Message>

    <Button
      v-if="loadState === 'loaded' && submitted && !showForm"
      label="Добавить реализацию"
      icon="pi pi-plus"
      variant="outlined"
      size="large"
      @click="openForm"
    />

    <ImplementationForm
      v-if="showForm"
      :project-type="projectType"
      :first="!submitted"
      :submit="submit"
      @edited="formEdited = true"
      @submitted="onSubmitted"
      @cancel="closeForm"
    />

    <!-- Only the list depends on the request; the header, specs and form are already shown. -->
    <div v-if="loadState === 'loading'" class="flex flex-col gap-2" aria-busy="true" aria-label="Загрузка реализаций">
      <Skeleton width="9.375rem" height="0.875rem" class="mx-1 my-0.5" />
      <Card class="overflow-hidden" :pt="{ body: { class: 'p-0' } }">
        <template #content>
          <div
            v-for="(width, index) in ['88%', '64%']"
            :key="width"
            class="flex flex-col gap-2 px-4 py-3.5"
            :class="{ 'border-t border-surface': index > 0 }"
          >
            <span class="flex gap-2">
              <Skeleton width="3.25rem" height="1.125rem" />
              <Skeleton width="6rem" height="1.125rem" />
            </span>
            <Skeleton :width="width" height="0.875rem" />
          </div>
        </template>
      </Card>
    </div>

    <Message v-if="loadState === 'failed'" severity="error" icon="pi pi-exclamation-circle" role="alert">
      <div class="flex flex-col items-start gap-3">
        <span>Не удалось загрузить реализации. Проверьте соединение и попробуйте ещё раз.</span>
        <Button
          label="Попробовать снова"
          icon="pi pi-refresh"
          severity="danger"
          variant="outlined"
          size="small"
          @click="load"
        />
      </div>
    </Message>

    <ListSection v-if="submitted" :title="`Мои реализации · ${implementations!.length}`">
      <ImplementationRow
        v-for="(implementation, index) in implementations"
        :key="implementation.id"
        :implementation="implementation"
        :divider="index > 0"
        :highlighted="implementation.id === highlightedId"
      />
    </ListSection>
  </div>
</template>
