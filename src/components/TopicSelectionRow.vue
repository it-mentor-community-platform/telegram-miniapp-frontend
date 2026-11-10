<script setup lang="ts">
import { computed, useId } from 'vue'
import ToggleButton from 'primevue/togglebutton'
import Message from 'primevue/message'
import Button from 'primevue/button'
import { RouterLink, type RouteLocationRaw } from 'vue-router'

const props = withDefaults(defineProps<{
  name: string
  questionCount: number
  selected: boolean
  learnedPercent: number
  pending: boolean
  error?: string
  showProgress?: boolean
  to?: RouteLocationRaw
}>(), { showProgress: true })
const emit = defineEmits<{ select: [selected: boolean]; refresh: [] }>()
const errorId = useId()
const questionLabel = computed(() => {
  const n = props.questionCount
  const ending = n % 100 >= 11 && n % 100 <= 14 ? 'вопросов'
    : n % 10 === 1 ? 'вопрос' : n % 10 >= 2 && n % 10 <= 4 ? 'вопроса' : 'вопросов'
  return `${n} ${ending}`
})
</script>

<template>
  <div class="flex min-w-0 flex-col justify-center gap-2 px-4 py-3">
    <div class="flex min-h-10 items-center gap-3">
      <component :is="to ? RouterLink : 'div'" :to="to" class="flex min-w-0 flex-1 flex-col gap-0.5 rounded-border text-color" :class="{ 'focus-ring hover:text-primary': to }">
        <span class="text-md font-semibold wrap-anywhere">{{ name }}</span>
        <span class="text-meta text-muted-color">
          {{ questionLabel }}<template v-if="selected && showProgress"> · выучено {{ learnedPercent }}%</template>
        </span>
      </component>
      <ToggleButton
        :model-value="selected"
        readonly
        :disabled="pending"
        :aria-busy="pending"
        :aria-label="`${selected ? 'Убрать с повторения' : 'Добавить на повторение'}: ${name}`"
        :aria-describedby="error ? errorId : undefined"
        on-label="На повторении"
        off-label="Добавить"
        class="min-h-11 shrink-0 text-meta"
        :dt="{
          root: {
            background: '{content.background}', borderColor: '{form.field.border.color}',
            color: '{text.color}', hoverBackground: '{content.hover.background}',
            checkedBackground: '{tint.success.background}', checkedBorderColor: '{tint.success.background}',
            checkedColor: '{tint.success.color}',
          },
          content: { checkedBackground: '{tint.success.background}', checkedShadow: 'none' },
        }"
        @click="!pending && emit('select', !selected)"
      >
        <i :class="['pi', pending ? 'pi-spinner pi-spin' : selected ? 'pi-check' : 'pi-plus']" aria-hidden="true" />
        <span>{{ selected ? 'На повторении' : 'Добавить' }}</span>
      </ToggleButton>
    </div>
    <div v-if="error" :id="errorId" class="flex flex-col items-start gap-1">
      <Message severity="error" variant="simple" size="small" role="alert">{{ error }}</Message>
      <Button label="Обновить данные" icon="pi pi-refresh" text size="small" @click="emit('refresh')" />
    </div>
  </div>
</template>
