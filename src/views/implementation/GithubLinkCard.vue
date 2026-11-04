<script setup lang="ts">
import { nextTick, ref, useId, useTemplateRef, watch } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { ConflictError } from '../../api'
import { canonicalGithubUrl, isGithubRepositoryUrl } from '../../roadmap'
import LinkView from './LinkView.vue'

// GitHub repository of an implementation; see design/Impl-EditGithub.dc.html, Impl-GithubTaken.dc.html.
const props = defineProps<{
  url: string
  save: (url: string) => Promise<void>
}>()

const editing = ref(false)
const draft = ref('')
const error = ref<string>()
const saveFailed = ref(false)
const saving = ref(false)

const inputId = useId()
const input = useTemplateRef<{ $el: HTMLInputElement }>('input')

// Editing the field clears its error.
watch(draft, () => (error.value = undefined))

async function startEdit() {
  draft.value = props.url
  saveFailed.value = false
  editing.value = true
  await nextTick()
  input.value?.$el.focus()
}

function cancel() {
  editing.value = false
  error.value = undefined
}

async function onSave() {
  if (saving.value) {
    return
  }
  const url = draft.value.trim()
  if (!isGithubRepositoryUrl(url)) {
    error.value = 'Укажите ссылку вида https://github.com/username/repo'
    return
  }
  // Unchanged: nothing to send.
  if (canonicalGithubUrl(url) === canonicalGithubUrl(props.url)) {
    cancel()
    return
  }

  saving.value = true
  saveFailed.value = false
  try {
    await props.save(url)
    cancel()
  } catch (saveError) {
    if (saveError instanceof ConflictError) {
      error.value = 'Этот репозиторий уже используется другой реализацией. Ссылка не изменена — сохранена прежняя.'
    } else {
      saveFailed.value = true
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Card>
    <template #content>
      <section class="flex flex-col gap-2.5" aria-label="GitHub-репозиторий">
        <span class="text-meta font-semibold text-(--p-tint-neutral-color)">GitHub-репозиторий</span>

        <LinkView v-if="!editing" :url="url" edit-label="Изменить ссылку на репозиторий" @edit="startEdit" />

        <form v-else class="flex flex-col gap-2.5" novalidate :aria-busy="saving" @submit.prevent="onSave">
          <div class="flex min-w-0 flex-col gap-0.5 rounded-lg bg-(--p-tint-neutral-background) px-3 py-2.5">
            <span class="text-note/4 text-muted-color">Текущая ссылка</span>
            <a
              :href="url"
              target="_blank"
              rel="noopener"
              class="focus-ring flex min-w-0 items-center gap-1.5 rounded-border text-sm font-medium text-primary"
            >
              <span class="truncate">{{ url.replace(/^https?:\/\//, '') }}</span>
              <i class="pi pi-external-link shrink-0 text-xs" aria-hidden="true" />
            </a>
          </div>

          <div class="flex flex-col gap-1.5">
            <label :for="inputId" class="text-meta font-semibold text-(--p-tint-neutral-color)">Новая ссылка</label>
            <InputText
              :id="inputId"
              ref="input"
              v-model="draft"
              type="url"
              inputmode="url"
              autocomplete="off"
              placeholder="https://github.com/username/repo"
              :invalid="Boolean(error)"
              :disabled="saving"
              fluid
            />
            <Message v-if="error" severity="error" size="small" variant="simple" icon="pi pi-exclamation-circle" role="alert">
              {{ error }}
            </Message>
            <small v-else class="text-note text-muted-color">
              Ссылка обновится после проверки: репозиторий должен быть публичным и не сданным ранее. Ревью и
              прогресс сохранятся.
            </small>
          </div>

          <Message v-if="saveFailed" severity="error" icon="pi pi-exclamation-circle" role="alert">
            Не удалось сохранить ссылку. Попробуйте ещё раз.
          </Message>

          <div class="grid grid-cols-2 gap-2">
            <Button label="Отмена" severity="secondary" variant="outlined" class="min-h-11 text-sm" :disabled="saving" @click="cancel" />
            <Button type="submit" label="Сохранить" class="min-h-11 text-sm" :loading="saving" />
          </div>
        </form>
      </section>
    </template>
  </Card>
</template>
