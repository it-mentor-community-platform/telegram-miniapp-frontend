<script setup lang="ts">
import { nextTick, ref, useId, useTemplateRef, watch } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { isHttpsUrl } from '../../roadmap'
import LinkView from './LinkView.vue'

// Deploy link of an implementation, for deployable project types; see design/Implementation.dc.html,
// Impl-NoDeploy.dc.html, Impl-EditDeploy.dc.html.
const props = defineProps<{
  url?: string
  // null removes the link.
  save: (url: string | null) => Promise<void>
}>()

const editing = ref(false)
const draft = ref('')
const error = ref<string>()
const saveFailed = ref(false)
// Which button is in flight.
const saving = ref<'save' | 'remove'>()

const inputId = useId()
const input = useTemplateRef<{ $el: HTMLInputElement }>('input')

watch(draft, () => (error.value = undefined))

async function startEdit() {
  draft.value = props.url ?? ''
  saveFailed.value = false
  editing.value = true
  await nextTick()
  input.value?.$el.focus()
}

function cancel() {
  editing.value = false
  error.value = undefined
}

async function send(url: string | null, action: 'save' | 'remove') {
  saving.value = action
  saveFailed.value = false
  try {
    await props.save(url)
    cancel()
  } catch {
    saveFailed.value = true
  } finally {
    saving.value = undefined
  }
}

function onSave() {
  if (saving.value) {
    return
  }
  const url = draft.value.trim()
  // An emptied field removes the link; with no link there is nothing to save.
  if (!url) {
    return props.url ? send(null, 'remove') : cancel()
  }
  if (!isHttpsUrl(url)) {
    error.value = 'Укажите ссылку, начинающуюся с https://'
    return
  }
  if (url === props.url) {
    return cancel()
  }
  return send(url, 'save')
}
</script>

<template>
  <Card>
    <template #content>
      <section class="flex flex-col gap-2.5" aria-label="Деплой">
        <span class="text-meta font-semibold text-(--p-tint-neutral-color)">Деплой</span>

        <form v-if="editing" class="flex flex-col gap-2.5" novalidate :aria-busy="Boolean(saving)" @submit.prevent="onSave">
          <div class="flex flex-col gap-1.5">
            <label :for="inputId" class="sr-only">Ссылка на деплой</label>
            <InputText
              :id="inputId"
              ref="input"
              v-model="draft"
              type="url"
              inputmode="url"
              autocomplete="off"
              placeholder="https://"
              :invalid="Boolean(error)"
              :disabled="Boolean(saving)"
              fluid
            />
            <Message v-if="error" severity="error" size="small" variant="simple" icon="pi pi-exclamation-circle" role="alert">
              {{ error }}
            </Message>
          </div>

          <Message v-if="saveFailed" severity="error" icon="pi pi-exclamation-circle" role="alert">
            Не удалось сохранить ссылку. Попробуйте ещё раз.
          </Message>

          <div class="grid grid-cols-2 gap-2">
            <Button
              label="Отмена"
              severity="secondary"
              variant="outlined"
              class="min-h-11 text-sm"
              :disabled="Boolean(saving)"
              @click="cancel"
            />
            <Button
              type="submit"
              label="Сохранить"
              class="min-h-11 text-sm"
              :loading="saving === 'save'"
              :disabled="saving === 'remove'"
            />
          </div>
          <Button
            v-if="url"
            label="Удалить ссылку на деплой"
            icon="pi pi-trash"
            severity="danger"
            text
            class="min-h-11 text-sm"
            :loading="saving === 'remove'"
            :disabled="saving === 'save'"
            @click="send(null, 'remove')"
          />
        </form>

        <LinkView v-else-if="url" :url="url" edit-label="Изменить ссылку на деплой" @edit="startEdit" />

        <div v-else class="flex items-center justify-between gap-2">
          <span class="text-sm text-muted-color">Ссылка не указана</span>
          <Button label="Добавить деплой" icon="pi pi-plus" variant="outlined" class="min-h-11 shrink-0 text-sm" @click="startEdit" />
        </div>

        <span class="text-note text-muted-color">Доступность сайта по ссылке не проверяется</span>
      </section>
    </template>
  </Card>
</template>
