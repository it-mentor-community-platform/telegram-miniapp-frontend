<script setup lang="ts">
import { computed, onBeforeUnmount } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import ProgressBar from 'primevue/progressbar'
import Skeleton from 'primevue/skeleton'
import Tag from 'primevue/tag'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import StatTiles from '../components/StatTiles.vue'
import { useBreadcrumbs } from '../composables/useBreadcrumbs'
import { useRepetitionTopics } from '../composables/useRepetitionTopics'
import { getTopicLearnedPercent } from '../mocks/repetition'

const router = useRouter()
const breadcrumbs = useBreadcrumbs()
const { selectedCategories, loading, loadError, load } = useRepetitionTopics()
const topics = computed(() => selectedCategories.value ?? [])
const due = computed(() => topics.value.reduce((sum, topic) => sum + topic.questions_ready_to_repeat, 0))
const fresh = computed(() => topics.value.reduce((sum, topic) => sum + topic.new_questions, 0))
const available = computed(() => due.value + fresh.value)
const repeatLabel = computed(() => {
  const n = available.value
  const word = n % 100 >= 11 && n % 100 <= 14 ? 'вопросов'
    : n % 10 === 1 ? 'вопрос' : n % 10 >= 2 && n % 10 <= 4 ? 'вопроса' : 'вопросов'
  return `Повторить всё · ${n} ${word}`
})
const stats = computed(() => [
  { value: due.value, label: 'к повторению', tone: 'warn' as const },
  { value: fresh.value, label: 'новых', tone: 'info' as const },
  { value: 0, label: 'выучено', tone: 'success' as const },
])
let active = true
onBeforeUnmount(() => { active = false })

async function refresh() {
  await load()
  // An unsuccessful request must never be treated as an empty selection.
  if (active && !loadError.value && selectedCategories.value?.length === 0) {
    await router.replace({ name: 'student-repetition-select' })
  }
}
void refresh()
</script>

<template>
  <div class="flex flex-col gap-5">
    <Breadcrumbs :items="breadcrumbs" />
    <header class="flex flex-wrap items-center gap-3">
      <h1 class="text-page font-bold">Повторение</h1>
      <Button :as="RouterLink" :to="{ name: 'student-repetition-topics' }" label="Все темы" icon="pi pi-plus" severity="secondary" variant="outlined" class="ml-auto" />
      <Button :as="available ? RouterLink : 'BUTTON'" :to="available ? { name: 'student-repetition-review' } : undefined" :label="repeatLabel" icon="pi pi-play" :disabled="!available" class="hidden md:inline-flex" />
    </header>

    <Message v-if="loadError" severity="error" icon="pi pi-exclamation-circle" role="alert">
      <div class="flex flex-col items-start gap-3">
        <span>{{ selectedCategories ? 'Не удалось обновить темы. Показаны ранее загруженные данные.' : 'Не удалось загрузить ваши темы. Проверьте соединение и попробуйте ещё раз.' }}</span>
        <Button label="Попробовать снова" icon="pi pi-refresh" severity="danger" variant="outlined" size="small" :loading="loading" @click="refresh" />
      </div>
    </Message>

    <div v-if="!selectedCategories" class="flex flex-col gap-4" :aria-busy="loading" aria-label="Загрузка выбранных тем">
      <Card v-if="loading"><template #content><Skeleton height="4rem" /></template></Card>
      <div v-if="loading" class="grid gap-3 md:grid-cols-2" aria-hidden="true">
        <Card v-for="item in 4" :key="item"><template #content><Skeleton height="6rem" /></template></Card>
      </div>
    </div>

    <template v-else-if="topics.length">
      <span v-if="loading" class="text-meta text-muted-color" role="status">Обновляем темы…</span>
      <Card>
        <template #content>
          <div class="flex flex-col gap-3">
            <StatTiles :items="stats" />
            <Button label="Статистика и активность" icon="pi pi-chart-line" severity="secondary" text disabled class="justify-start" />
          </div>
        </template>
      </Card>

      <section class="flex flex-col gap-2" aria-labelledby="my-topics-title">
        <h2 id="my-topics-title" class="px-1 text-meta font-semibold tracking-[0.04em] text-muted-color uppercase">Мои темы · {{ topics.length }}</h2>
        <div class="grid gap-3 md:grid-cols-2">
          <Card v-for="topic in topics" :key="topic.id">
            <template #content>
              <div class="flex flex-col gap-3">
                <div class="flex items-center gap-3">
                  <RouterLink :to="{ name: 'student-repetition-topic', params: { topicId: topic.id } }" class="focus-ring flex min-w-0 flex-1 flex-col gap-1 rounded-border text-color hover:text-primary">
                    <div class="flex flex-wrap items-center gap-2">
                      <h3 class="text-base font-semibold wrap-anywhere">{{ topic.name }}</h3>
                      <Tag :value="topic.specialization" severity="secondary" class="text-note" />
                    </div>
                    <p v-if="topic.new_questions + topic.questions_ready_to_repeat > 0" class="text-meta text-muted-color">
                      <span class="font-semibold text-(--p-tint-warn-color)">{{ topic.questions_ready_to_repeat }}</span> к повторению ·
                      <span class="font-semibold text-(--p-tint-info-color)">{{ topic.new_questions }}</span> новых · {{ topic.all_questions }} всего
                    </p>
                    <p v-else class="text-meta text-muted-color">Всё повторено</p>
                  </RouterLink>
                  <Button v-if="topic.new_questions + topic.questions_ready_to_repeat > 0" :as="RouterLink" :to="{ name: 'student-repetition-review', query: { topic: topic.id } }" icon="pi pi-play" rounded :aria-label="`Повторить тему ${topic.name}`" />
                  <span v-else class="tint-success flex size-11 shrink-0 items-center justify-center rounded-full" role="img" aria-label="Всё повторено"><i class="pi pi-check" aria-hidden="true" /></span>
                </div>
                <div class="flex flex-col gap-1.5">
                  <div class="flex justify-between text-note text-muted-color"><span>Выучено 0 из {{ topic.all_questions }}</span><span>{{ getTopicLearnedPercent() }}%</span></div>
                  <ProgressBar :value="getTopicLearnedPercent()" :show-value="false" class="h-1.5" :aria-label="`Выучено в теме ${topic.name}`" />
                </div>
              </div>
            </template>
          </Card>
        </div>
      </section>
      <Button :as="available ? RouterLink : 'BUTTON'" :to="available ? { name: 'student-repetition-review' } : undefined" :label="repeatLabel" icon="pi pi-play" :disabled="!available" class="md:hidden" />
    </template>
  </div>
</template>
