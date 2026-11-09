<script setup lang="ts">
import { computed, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import ProgressBar from 'primevue/progressbar'
import Skeleton from 'primevue/skeleton'
import Tag from 'primevue/tag'
import NotFoundState from '../components/NotFoundState.vue'
import { useRepetitionReview, type ReviewScope } from '../composables/useRepetitionReview'
import { useRepetitionTopics } from '../composables/useRepetitionTopics'
import { REVIEW_RATINGS } from '../repetition'
import { getReviewPlaceholders } from '../mocks/repetition'

const route = useRoute()
const scope = computed<ReviewScope>(() => {
  const value = route.query.topic
  if (value === undefined) return { valid: true }
  if (typeof value !== 'string' || !/^[1-9]\d*$/.test(value) || !Number.isSafeInteger(Number(value))) return { valid: false }
  return { valid: true, topicId: Number(value) }
})
const { question, revealed, phase, answers, unconfirmed, remaining, completed, total, progress, summary, topicCount, reveal, hide, rate, loadNext } = useRepetitionReview(scope)
const { specializations, load: loadCatalog } = useRepetitionTopics()
watch(scope, (value) => { if (value.valid) void loadCatalog() }, { immediate: true })
const category = computed(() => {
  const id = question.value?.categoryId ?? (scope.value.valid ? scope.value.topicId : undefined)
  for (const group of specializations.value ?? []) {
    const topic = group.categories.find((item) => item.id === id)
    if (topic) return { name: topic.name, specialization: group.name }
  }
  return undefined
})
const title = computed(() => scope.value.valid && scope.value.topicId !== undefined ? category.value?.name ?? 'Повторить тему' : 'Повторить всё')
const canRate = computed(() => Boolean(question.value) && ['question', 'save-error'].includes(phase.value))
const placeholders = getReviewPlaceholders()
const isEmpty = computed(() => answers.value.length === 0 && unconfirmed.value === 0)
const referenceUrl = computed(() => /^Java(?:\s+Backend)?$/i.test(category.value?.specialization ?? '')
  ? 'https://zhukovsd.github.io/java-backend-interview-prep/' : undefined)
</script>

<template>
  <div class="mx-auto flex w-full max-w-160 flex-1 flex-col gap-5">
    <header class="flex items-center gap-2">
      <Button :as="RouterLink" :to="{ name: 'student-repetition' }" icon="pi pi-times" text rounded severity="secondary" aria-label="Завершить повторение" class="size-11 shrink-0" />
      <h1 class="min-w-0 flex-1 text-center text-base font-semibold wrap-anywhere">{{ title }}</h1>
      <span class="size-11 shrink-0" aria-hidden="true" />
    </header>

    <NotFoundState v-if="phase === 'not-found'" title="Тема не найдена" text="Проверьте ссылку или выберите другую тему для повторения." :action="{ label: 'К моим темам', to: { name: 'student-repetition' } }" />

    <template v-else-if="phase === 'done'">
      <div class="flex flex-col items-center gap-3 py-4 text-center" role="status">
        <Avatar :icon="isEmpty ? 'pi pi-calendar' : 'pi pi-check'" shape="circle" class="tint-success size-18" :dt="{ icon: { size: '2rem' } }" aria-hidden="true" />
        <h2 class="text-2xl font-bold">{{ isEmpty ? 'Пока нечего повторять' : 'На сегодня всё' }}</h2>
        <p class="text-md text-muted-color">{{ isEmpty ? 'В выбранных темах нет новых вопросов или вопросов, готовых к повторению.' : `Подтверждено ответов: ${answers.length}. Тем: ${topicCount}.` }}</p>
        <p v-if="!isEmpty" class="text-meta text-muted-color">{{ placeholders.streak }}</p>
      </div>
      <Message v-if="unconfirmed" severity="warn">Ответов с неподтверждённым сохранением: {{ unconfirmed }}. В распределении оценок они не учитываются.</Message>
      <Card v-if="!isEmpty">
        <template #content>
          <div class="flex flex-col gap-3">
            <h3 class="text-meta font-semibold text-muted-color uppercase">Ваши оценки</h3>
            <div v-for="item in [...summary].reverse()" :key="item.quality" class="grid grid-cols-[6.5rem_minmax(0,1fr)_1.75rem] items-center gap-3">
              <span class="text-sm">{{ item.label }}</span>
              <ProgressBar :value="answers.length ? item.count / answers.length * 100 : 0" :show-value="false" class="h-2" :aria-label="item.label" />
              <span class="text-right text-sm font-semibold">{{ item.count }}</span>
            </div>
          </div>
        </template>
      </Card>
      <p class="flex items-start gap-2 rounded-xl bg-emphasis p-4 text-sm text-muted-color"><i class="pi pi-calendar mt-0.5" aria-hidden="true" />{{ placeholders.forecast }}</p>
      <div class="mt-auto flex flex-col gap-2 pt-4">
        <Button :as="RouterLink" :to="{ name: 'student-repetition' }" label="К моим темам" class="min-h-12" />
        <Button :as="RouterLink" :to="{ name: 'home' }" label="На главную" text />
      </div>
    </template>

    <template v-else>
      <div v-if="total" class="flex flex-col gap-2">
        <div class="flex justify-between text-meta text-muted-color"><span>Вопрос {{ Math.min(completed + 1, total) }} из {{ total }}</span><span>осталось {{ question?.questions_left ?? remaining }}</span></div>
        <ProgressBar :value="progress" :show-value="false" class="h-1.5" aria-label="Прогресс повторения" />
      </div>
      <Message v-if="phase === 'load-error'" severity="error" role="alert">
        <div class="flex flex-col items-start gap-3"><span>Не удалось загрузить следующий вопрос. Сохранённые оценки не потеряны.</span><Button label="Попробовать снова" icon="pi pi-refresh" severity="danger" variant="outlined" size="small" @click="loadNext" /></div>
      </Message>
      <Message v-if="phase === 'save-error'" severity="error" role="alert"><div class="flex flex-col items-start gap-3"><span>Сервис отклонил оценку. Попробуйте ещё раз или обновите вопрос.</span><Button label="Обновить вопрос" icon="pi pi-refresh" severity="danger" variant="outlined" size="small" @click="loadNext" /></div></Message>
      <Message v-if="phase === 'uncertain'" severity="warn" role="alert">
        <div class="flex flex-col items-start gap-3"><span>Не удалось подтвердить сохранение оценки. Повторная отправка заблокирована, чтобы не записать ответ дважды. Проверьте очередь или вернитесь к моим темам.</span><Button label="Проверить очередь" icon="pi pi-refresh" severity="secondary" variant="outlined" size="small" @click="loadNext" /></div>
      </Message>
      <div v-if="phase === 'loading'" class="flex flex-col gap-4" role="status" aria-label="Загрузка вопроса" aria-busy="true"><Skeleton width="8rem" height="1.5rem" /><Skeleton height="5rem" /><Skeleton width="9rem" height="2.75rem" /></div>
      <template v-else-if="question">
        <Card>
          <template #content>
            <div class="flex flex-col gap-3">
              <div class="text-center"><h3 class="text-md font-semibold">Насколько хорошо вы помните ответ?</h3><p class="mt-1 text-meta text-muted-color">Оценивайте честно — от этого зависит расписание</p></div>
              <span v-if="phase === 'saving'" class="text-center text-meta text-muted-color" role="status"><i class="pi pi-spinner pi-spin mr-2" aria-hidden="true" />Сохраняем оценку…</span>
              <div class="grid grid-cols-2 gap-2"><Button v-for="rating in REVIEW_RATINGS" :key="rating.quality" severity="secondary" variant="outlined" class="min-h-15" :disabled="!canRate" :loading="phase === 'saving'" @click="rate(rating.quality)"><span class="flex flex-col gap-0.5"><span class="font-semibold">{{ rating.label }}</span><span class="text-note text-muted-color">{{ placeholders.interval }}</span></span></Button></div>
            </div>
          </template>
        </Card>
        <section class="flex flex-col gap-4" aria-label="Текущий вопрос">
          <div class="flex flex-wrap gap-2"><Tag :value="category?.name ?? `Тема ${question.categoryId}`" severity="secondary" /></div>
          <h2 class="text-page leading-snug font-bold wrap-anywhere">{{ question.title }}</h2>
          <template v-if="!revealed">
            <Button label="Показать ответ" icon="pi pi-eye" variant="outlined" class="self-start" :disabled="phase !== 'question'" @click="reveal" />
            <p class="text-sm text-muted-color">Сначала попробуйте ответить вслух или про себя, затем сверьтесь с ответом из методички.</p>
          </template>
          <Card v-else>
            <template #content>
              <div class="flex flex-col gap-3">
                <h3 class="text-note font-semibold tracking-wide text-muted-color uppercase">Ответ из методички</h3>
                <p class="text-md leading-relaxed whitespace-pre-wrap wrap-anywhere">{{ question.answer }}</p>
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <a v-if="referenceUrl" :href="referenceUrl" target="_blank" rel="noopener noreferrer" class="focus-ring inline-flex min-h-11 items-center gap-1 self-start rounded-border text-sm font-medium text-primary">Открыть в методичке <i class="pi pi-external-link text-xs" aria-hidden="true" /></a>
                  <Button label="Скрыть ответ" severity="secondary" text :disabled="phase !== 'question'" class="ml-auto" @click="hide" />
                </div>
              </div>
            </template>
          </Card>
        </section>
      </template>
    </template>
  </div>
</template>
