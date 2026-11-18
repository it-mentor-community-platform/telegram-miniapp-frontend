<script setup lang="ts">
import { computed, onBeforeUnmount } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import ProgressBar from 'primevue/progressbar'
import Skeleton from 'primevue/skeleton'
import Tag from 'primevue/tag'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import RepetitionLoadError from '../components/RepetitionLoadError.vue'
import StatTiles from '../components/StatTiles.vue'
import RepetitionStatsSkeleton from '../components/RepetitionStatsSkeleton.vue'
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
  <div class="flex flex-1 flex-col gap-5">
    <Breadcrumbs :items="breadcrumbs" />
    <header class="flex flex-wrap items-center gap-3">
      <h1 class="text-page font-bold">Повторение</h1>
      <Button :as="RouterLink" :to="{ name: 'student-repetition-topics' }" label="Все темы" icon="pi pi-plus" severity="secondary" variant="outlined" class="ml-auto" />
      <Button v-if="selectedCategories && !loadError" :as="available ? RouterLink : 'BUTTON'" :to="available ? { name: 'student-repetition-review' } : undefined" :label="repeatLabel" icon="pi pi-play" :disabled="!available" class="hidden md:inline-flex" />
    </header>

    <RepetitionLoadError v-if="loadError" text="Не удалось загрузить ваши темы. Проверьте соединение и попробуйте ещё раз." :loading="loading" @retry="refresh" />

    <div v-if="!selectedCategories && loading" class="flex flex-col gap-5" role="status" aria-busy="true" aria-label="Загрузка выбранных тем">
      <Card class="overflow-hidden" :pt="{ body: { class: 'p-0' } }">
        <template #content>
          <div class="p-4"><RepetitionStatsSkeleton /></div>
          <div class="flex min-h-12 items-center justify-between gap-3 border-t border-surface px-4" aria-hidden="true">
            <Skeleton width="10.625rem" height="0.875rem" /><Skeleton width="5rem" height="0.75rem" />
          </div>
        </template>
      </Card>
      <section class="flex flex-col gap-2" aria-label="Загрузка тем">
        <h2 class="px-1 text-meta font-semibold tracking-[0.04em] text-muted-color uppercase">Мои темы</h2>
        <div class="grid gap-2.5 md:grid-cols-2" aria-hidden="true">
          <Card v-for="(width, index) in ['40%', '55%', '35%']" :key="index" :pt="{ body: { class: 'px-4 py-3.5' } }">
            <template #content>
              <div class="flex flex-col gap-3.5">
                <div class="flex items-center gap-3">
                  <div class="flex min-w-0 flex-1 flex-col gap-2">
                    <div class="flex items-center gap-2"><Skeleton :width="width" height="1.125rem" /><Skeleton width="2.5rem" height="1.125rem" /></div>
                    <Skeleton width="75%" height="0.8125rem" />
                  </div>
                  <Skeleton shape="circle" size="2.75rem" class="shrink-0" />
                </div>
                <Skeleton height="0.375rem" />
              </div>
            </template>
          </Card>
        </div>
      </section>
    </div>

    <template v-else-if="!loadError && topics.length">
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
    </template>
    <div class="sticky bottom-0 z-10 -mx-4 mt-auto border-t border-surface bg-(--p-content-background) px-4 pt-3 pb-5 md:hidden">
      <Button :as="available && !loading && !loadError ? RouterLink : 'BUTTON'" :to="available && !loading && !loadError ? { name: 'student-repetition-review' } : undefined" :label="loading || loadError ? 'Повторить всё' : repeatLabel" icon="pi pi-play" :disabled="!available || loading || !!loadError" class="min-h-13 w-full" />
    </div>
  </div>
</template>
