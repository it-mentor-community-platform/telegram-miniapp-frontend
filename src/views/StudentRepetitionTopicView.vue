<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Accordion from 'primevue/accordion'
import AccordionPanel from 'primevue/accordionpanel'
import AccordionHeader from 'primevue/accordionheader'
import AccordionContent from 'primevue/accordioncontent'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'
import Tag from 'primevue/tag'
import { ConflictError, NotFoundError } from '../api'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import EmptyState from '../components/EmptyState.vue'
import NotFoundState from '../components/NotFoundState.vue'
import StatTiles from '../components/StatTiles.vue'
import { useBreadcrumbs } from '../composables/useBreadcrumbs'
import { useRepetitionTopic } from '../composables/useRepetitionTopic'
import { useRepetitionTopics } from '../composables/useRepetitionTopics'
import { getQuestionStatus } from '../mocks/repetition'

const route = useRoute()
const breadcrumbs = useBreadcrumbs()
const topicId = computed(() => {
  const value = String(route.params.topicId)
  const id = Number(value)
  return /^[1-9]\d*$/.test(value) && Number.isSafeInteger(id) ? id : undefined
})
const { topic, loading, error, notFound, load } = useRepetitionTopic(topicId)
const { specializations, loading: catalogLoading, loadError: catalogError, pendingIds, actionErrors, load: loadCatalog, setSelected } = useRepetitionTopics()
const selected = computed(() => {
  if (!specializations.value) return undefined
  return specializations.value.some((group) => group.categories.some((item) => item.id === topicId.value && item.selected))
})
const pending = computed(() => topicId.value !== undefined && pendingIds.value.has(topicId.value))
const selectionError = computed(() => {
  const cause = topicId.value === undefined ? undefined : actionErrors.value.get(topicId.value)
  if (!cause) return undefined
  if (cause instanceof ConflictError) return 'Тема уже добавлена. Обновите данные.'
  if (cause instanceof NotFoundError) return 'Тема больше недоступна. Обновите данные.'
  return 'Не удалось изменить выбор темы. Проверьте соединение и попробуйте ещё раз.'
})
const stats = computed(() => [
  { value: topic.value?.questions_ready_to_repeat ?? 0, label: 'к повторению', tone: 'warn' as const },
  { value: topic.value?.new_questions ?? 0, label: 'новых', tone: 'info' as const },
  { value: 0, label: 'выучено', tone: 'success' as const },
])
const available = computed(() => (topic.value?.new_questions ?? 0) + (topic.value?.questions_ready_to_repeat ?? 0))
const visibleCount = ref(8)
const opened = ref<string>()
const questions = computed(() => topic.value?.questions.slice(0, visibleCount.value) ?? [])
const remaining = computed(() => Math.max(0, (topic.value?.questions.length ?? 0) - visibleCount.value))
// Only the Java reference is specified in the mockup; do not invent source URLs for other tracks.
const referenceUrl = computed(() => /^Java(?:\s+Backend)?$/i.test(topic.value?.specialization ?? '')
  ? 'https://zhukovsd.github.io/java-backend-interview-prep/' : undefined)

function questionCount(count: number) {
  const word = count % 100 >= 11 && count % 100 <= 14 ? 'вопросов'
    : count % 10 === 1 ? 'вопрос' : count % 10 >= 2 && count % 10 <= 4 ? 'вопроса' : 'вопросов'
  return `${count} ${word}`
}

function changeSelection() {
  if (topicId.value !== undefined && selected.value !== undefined) {
    void setSelected(topicId.value, !selected.value)
  }
}

async function refresh() {
  await Promise.all([load(), loadCatalog()])
}

watch(topicId, (id) => {
  visibleCount.value = 8
  opened.value = undefined
  if (id !== undefined) void loadCatalog()
}, { immediate: true })
</script>

<template>
  <div class="flex flex-1 flex-col gap-4">
    <Breadcrumbs :items="breadcrumbs" />
    <NotFoundState
      v-if="notFound" title="Тема не найдена" text="Возможно, тема была удалена или ссылка указана неверно."
      :action="{ label: 'Ко всем темам', to: { name: 'student-repetition-topics' } }"
    />
    <template v-else>
      <Message v-if="error" severity="error" icon="pi pi-exclamation-circle" role="alert">
        <div class="flex flex-col items-start gap-3">
          <span>Не удалось загрузить тему. Проверьте соединение и попробуйте ещё раз.</span>
          <Button label="Попробовать снова" icon="pi pi-refresh" severity="danger" variant="outlined" size="small" :loading="loading" @click="refresh" />
        </div>
      </Message>
      <div v-if="!topic && loading" class="flex flex-col gap-4" role="status" aria-label="Загрузка темы" aria-busy="true">
        <Skeleton width="7rem" height="1.5rem" /><Skeleton width="60%" height="2rem" />
        <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_24.5rem]" aria-hidden="true">
          <Card><template #content><div class="flex flex-col gap-4"><Skeleton v-for="item in 5" :key="item" height="3rem" /></div></template></Card>
          <Card><template #content><Skeleton height="10rem" /></template></Card>
        </div>
      </div>

      <template v-if="topic">
        <header class="flex flex-col items-start gap-2">
          <Tag :value="topic.specialization" severity="secondary" />
          <h1 class="text-2xl font-bold wrap-anywhere">{{ topic.name }}</h1>
          <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-color">
            <span>{{ questionCount(topic.all_questions) }}</span>
            <a v-if="referenceUrl" :href="referenceUrl" target="_blank" rel="noopener noreferrer" class="focus-ring inline-flex min-h-11 items-center gap-1 rounded-border font-medium text-primary">
              Открыть в методичке <i class="pi pi-external-link text-xs" aria-hidden="true" />
            </a>
          </div>
        </header>
        <div class="grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_24.5rem] lg:gap-x-6 lg:gap-y-2">
          <aside class="flex min-w-0 flex-col gap-3 lg:col-start-2 lg:row-start-2" aria-label="Повторение темы">
            <Card>
              <template #content>
                <div class="flex flex-col gap-4">
                  <template v-if="selected === undefined">
                    <Skeleton v-if="catalogLoading" height="7rem" aria-label="Загрузка состояния подписки" />
                    <p v-else class="text-sm text-muted-color">Не удалось узнать, добавлена ли тема на повторение.</p>
                  </template>
                  <template v-else-if="selected">
                    <StatTiles :items="stats" />
                    <div class="flex flex-col gap-1">
                      <Button :label="`Повторить тему · ${questionCount(available)}`" icon="pi pi-play" disabled />
                      <Button label="Убрать с повторения" severity="secondary" text :loading="pending" @click="changeSelection" />
                    </div>
                  </template>
                  <template v-else>
                    <p class="text-sm text-muted-color">Просмотрите вопросы и ответы, а затем добавьте тему — вопросы будут попадать в очередь повторения по расписанию.</p>
                    <Button label="Добавить на повторение" icon="pi pi-plus" :loading="pending" @click="changeSelection" />
                  </template>
                  <Message v-if="selectionError" severity="error" variant="simple" size="small" role="alert">{{ selectionError }}</Message>
                  <Message v-if="catalogError" severity="error" variant="simple" size="small" role="alert">Не удалось обновить состояние подписки.</Message>
                  <Button v-if="selectionError || catalogError" label="Обновить данные" icon="pi pi-refresh" severity="secondary" variant="outlined" size="small" :loading="catalogLoading" :disabled="pending" @click="loadCatalog" />
                </div>
              </template>
            </Card>
          </aside>

          <section class="flex min-w-0 flex-col gap-2 lg:contents" aria-labelledby="topic-questions-title">
            <h2 id="topic-questions-title" class="px-1 text-meta font-semibold tracking-[0.04em] text-muted-color uppercase lg:col-start-1 lg:row-start-1">Вопросы</h2>
            <EmptyState v-if="!topic.questions.length" class="lg:col-start-1 lg:row-start-2" title="Вопросов пока нет" text="Когда в теме появятся вопросы, они будут доступны здесь." icon="info" />
            <Card v-else class="overflow-hidden lg:col-start-1 lg:row-start-2" :pt="{ body: { class: 'p-0' } }">
              <template #content>
                <Accordion :key="topic.id" v-model:value="opened">
                  <AccordionPanel v-for="question in questions" :key="question.id" :value="String(question.id)">
                    <AccordionHeader :pt="{ root: { class: 'items-start gap-3 text-md font-medium' } }">
                      <span class="flex min-w-0 flex-1 items-start gap-3">
                        <span class="mt-1.5 size-2 shrink-0 rounded-full bg-current text-subtle-color" aria-hidden="true" />
                        <span class="flex min-w-0 flex-col gap-1">
                          <span class="wrap-anywhere">{{ question.title }}</span>
                          <span class="text-note font-medium text-muted-color">{{ getQuestionStatus() }}</span>
                        </span>
                      </span>
                    </AccordionHeader>
                    <AccordionContent>
                      <p class="pl-5 text-sm leading-relaxed whitespace-pre-wrap wrap-anywhere">{{ question.answer }}</p>
                    </AccordionContent>
                  </AccordionPanel>
                </Accordion>
                <Button v-if="remaining" :label="`Показать ещё ${questionCount(remaining)}`" text class="min-h-12 w-full rounded-none" @click="visibleCount = topic.questions.length" />
              </template>
            </Card>
          </section>
        </div>
      </template>
    </template>
  </div>
</template>
