<script setup lang="ts">
import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import { RouterLink, useRouter, onBeforeRouteLeave } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import SelectButton from 'primevue/selectbutton'
import Skeleton from 'primevue/skeleton'
import { ConflictError, NotFoundError } from '../api'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import RepetitionLoadError from '../components/RepetitionLoadError.vue'
import EmptyState from '../components/EmptyState.vue'
import TopicSelectionRow from '../components/TopicSelectionRow.vue'
import { useBreadcrumbs } from '../composables/useBreadcrumbs'
import { useRepetitionTopics } from '../composables/useRepetitionTopics'
import { getTopicLearnedPercent } from '../mocks/repetition'

const props = withDefaults(defineProps<{ onboarding?: boolean }>(), { onboarding: false })
const router = useRouter()
const breadcrumbs = useBreadcrumbs()
const { specializations, selectedCategories, loading, loadError, pendingIds, actionErrors, load, setSelected, addSelectedCategories } = useRepetitionTopics()
// Unsaved onboarding choices exist only in this page instance, never in the shared catalog/storage.
const draft = ref(new Set<number>())
const saving = ref(false)
const saveError = shallowRef<unknown>()
let active = true
onBeforeUnmount(() => { active = false })
onBeforeRouteLeave(() => { draft.value = new Set() })
watch(() => props.onboarding, () => {
  draft.value = new Set()
  saveError.value = undefined
  void refresh()
})
watch(specializations, (value) => {
  if (!value) draft.value = new Set()
})

function isSelected(id: number, persisted: boolean) {
  return props.onboarding ? draft.value.has(id) : persisted
}

function selectTopic(id: number, selected: boolean) {
  if (!props.onboarding) return setSelected(id, selected)
  if (saving.value) return
  if (selected) draft.value.add(id)
  else draft.value.delete(id)
  saveError.value = undefined
}

async function continueSelection() {
  if (saving.value || !draft.value.size) return
  saving.value = true
  saveError.value = undefined
  try {
    const saved = await addSelectedCategories([...draft.value])
    if (saved && active && props.onboarding) await router.replace({ name: 'student-repetition' })
  } catch (error) {
    saveError.value = error
  } finally {
    saving.value = false
  }
}

const saveErrorText = computed(() => saveError.value instanceof ConflictError
  ? 'Часть тем уже выбрана. Обновите данные, чтобы продолжить.'
  : saveError.value instanceof NotFoundError
    ? 'Некоторые темы больше недоступны. Обновите данные и проверьте выбор.'
    : 'Не удалось сохранить выбранные темы. Проверьте соединение и попробуйте ещё раз.')
const search = ref('')
const specializationId = ref<number | null>(null)
const filterOptions = computed(() => [
  { label: 'Все', value: null },
  ...(specializations.value ?? []).map((item) => ({
    label: item.name.replace(/\s+Backend$/i, ''), value: item.id,
  })),
])
const groups = computed(() => {
  const query = search.value.trim().toLocaleLowerCase('ru')
  return (specializations.value ?? [])
    .filter((group) => specializationId.value === null || group.id === specializationId.value)
    .map((group) => ({
      ...group,
      selectedCount: group.categories.filter((category) => isSelected(category.id, category.selected)).length,
      totalCount: group.categories.length,
      categories: group.categories.filter((category) => category.name.toLocaleLowerCase('ru').includes(query)),
    }))
    .filter((group) => group.categories.length > 0)
})
const hasTopics = computed(() => specializations.value?.some((group) => group.categories.length > 0))
const filtered = computed(() => Boolean(search.value.trim()) || specializationId.value !== null)

function actionError(categoryId: number): string | undefined {
  const error = actionErrors.value.get(categoryId)
  if (!error) return undefined
  if (error instanceof ConflictError) return 'Тема уже добавлена. Обновите данные.'
  if (error instanceof NotFoundError) return 'Тема не найдена. Обновите данные.'
  return 'Не удалось изменить выбор темы. Проверьте соединение и попробуйте ещё раз.'
}

function resetFilters() {
  search.value = ''
  specializationId.value = null
}

async function refresh() {
  await load()
  if (!active) return
  if (!loadError.value && selectedCategories.value) {
    if (props.onboarding && selectedCategories.value.length > 0) {
      await router.replace({ name: 'student-repetition' })
      return
    }
    if (!props.onboarding && selectedCategories.value.length === 0) {
      await router.replace({ name: 'student-repetition-select' })
      return
    }
    // Remove draft IDs for topics that disappeared during a successful refresh.
    const availableIds = new Set(specializations.value?.flatMap((group) => group.categories.map((category) => category.id)))
    draft.value = new Set([...draft.value].filter((id) => availableIds.has(id)))
    saveError.value = undefined
  }
  if (specializations.value && !specializations.value.some((group) => group.id === specializationId.value)) {
    specializationId.value = null
  }
}

void refresh()
</script>

<template>
  <div class="flex flex-col gap-4">
    <header class="flex flex-col gap-1">
      <Breadcrumbs :items="onboarding ? [] : breadcrumbs" />
      <h1 class="text-page font-bold">Все темы</h1>
      <p class="text-sm text-muted-color">{{ onboarding ? 'Выберите интересные темы и нажмите «Продолжить»' : 'Добавьте темы, вопросы из которых хотите повторять' }}</p>
    </header>

    <div class="flex min-w-0 flex-col gap-3 md:flex-row md:flex-wrap md:items-center">
      <IconField class="min-w-0 md:min-w-48 md:flex-1">
        <InputIcon class="pi pi-search" aria-hidden="true" />
        <InputText
          v-model="search" type="search" placeholder="Поиск по темам" aria-label="Поиск по темам"
          class="min-h-11 w-full" :disabled="!specializations"
        />
      </IconField>
      <div class="min-w-0 overflow-x-auto md:max-w-full">
        <SelectButton
          v-model="specializationId" :options="filterOptions" option-label="label" option-value="value"
          :allow-empty="false" :disabled="!specializations" aria-label="Специализация"
          class="min-w-full" :pt="{ pcToggleButton: { root: { class: 'min-h-11 flex-1 whitespace-nowrap' } } }"
        />
      </div>
    </div>

    <RepetitionLoadError v-if="loadError" text="Не удалось загрузить список тем. Проверьте соединение и попробуйте ещё раз." :loading="loading" :disabled="saving" @retry="refresh" />

    <div v-if="!specializations && loading" class="flex flex-col gap-5" role="status" aria-label="Загрузка тем" aria-busy="true">
      <section v-for="(count, group) in [5, 3]" :key="group" class="flex flex-col gap-2" aria-hidden="true">
        <div class="flex justify-between gap-3 px-1 py-0.5"><Skeleton :width="group ? '9.375rem' : '8.125rem'" height="0.875rem" /><Skeleton width="5.625rem" height="0.875rem" /></div>
        <Card class="overflow-hidden" :pt="{ body: { class: 'p-0' } }">
          <template #content>
            <div class="grid grid-cols-1 md:grid-cols-2">
              <div v-for="row in count" :key="row" class="flex min-h-16 items-center gap-3 border-surface py-2.5 pr-3 pl-4" :class="{ 'border-t md:border-t-0': row === 2, 'border-t': row > 2, 'md:border-l': row % 2 === 0 }">
                <div class="flex min-w-0 flex-1 flex-col gap-1.75"><Skeleton :width="['40%', '55%', '35%', '60%'][(row - 1) % 4]" height="0.9375rem" /><Skeleton :width="['30%', '45%', '38%', '28%'][(row - 1) % 4]" height="0.75rem" /></div>
                <Skeleton width="6.5rem" height="2.25rem" class="shrink-0" />
              </div>
            </div>
          </template>
        </Card>
      </section>
    </div>

    <template v-if="specializations && !loadError">
      <span v-if="loading" class="text-meta text-muted-color" role="status">Обновляем темы…</span>
      <section v-for="group in groups" :key="group.id" class="flex flex-col gap-2" :aria-labelledby="`specialization-${group.id}`">
        <h2 :id="`specialization-${group.id}`" class="flex items-baseline justify-between gap-3 px-1 text-meta text-muted-color">
          <span class="font-semibold tracking-[0.04em] uppercase">{{ group.name }}</span>
          <span class="shrink-0 text-right">на повторении {{ group.selectedCount }} из {{ group.totalCount }}</span>
        </h2>
        <Card class="overflow-hidden" :pt="{ body: { class: 'p-0' } }">
          <template #content>
            <ul class="grid grid-cols-1 md:grid-cols-2">
              <li v-for="(category, index) in group.categories" :key="category.id" class="min-w-0 border-surface" :class="{ 'border-t md:border-t-0': index === 1, 'border-t': index > 1, 'md:border-l': index % 2 === 1 }">
                <TopicSelectionRow
                  :name="category.name" :question-count="category.all_questions" :selected="isSelected(category.id, category.selected)"
                  :show-progress="!onboarding"
                  :to="onboarding ? undefined : { name: 'student-repetition-topic', params: { topicId: category.id } }"
                  :learned-percent="getTopicLearnedPercent()" :pending="onboarding ? saving : pendingIds.has(category.id)"
                  :error="onboarding ? undefined : actionError(category.id)" @select="selectTopic(category.id, $event)" @refresh="refresh"
                />
              </li>
            </ul>
          </template>
        </Card>
      </section>
      <template v-if="groups.length === 0">
        <EmptyState
          icon="info" :title="hasTopics ? 'Ничего не найдено' : 'Тем пока нет'"
          :text="hasTopics ? 'Попробуйте изменить поисковый запрос или выбрать другую специализацию.' : 'Когда появятся темы для повторения, они будут доступны здесь.'"
        />
        <Button v-if="filtered" label="Сбросить фильтры" icon="pi pi-filter-slash" severity="secondary" variant="outlined" class="self-start" @click="resetFilters" />
      </template>
    </template>
    <div v-if="onboarding" class="sticky bottom-0 z-10 -mx-4 mt-auto flex flex-col gap-3 border-t border-surface bg-(--p-content-background) px-4 py-4 md:mx-0 md:rounded-xl md:border" aria-label="Сохранение выбранных тем">
      <Message v-if="saveError" severity="error" role="alert">
        <div class="flex flex-col items-start gap-2">
          <span>{{ saveErrorText }}</span>
          <Button label="Обновить данные" icon="pi pi-refresh" severity="danger" text size="small" :loading="loading" :disabled="saving" @click="refresh" />
        </div>
      </Message>
      <Button :label="`Продолжить · выбрано ${draft.size}`" :disabled="!draft.size || !specializations || loading" :loading="saving" @click="continueSelection" />
      <RouterLink :to="{ name: 'home' }" class="focus-ring self-center rounded-border px-3 py-2 text-sm text-muted-color">На главную</RouterLink>
    </div>
  </div>
</template>
