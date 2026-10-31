<script setup lang="ts">
import { computed, ref, useId, watch } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import SelectButton from 'primevue/selectbutton'
import { ConflictError } from '../../api'
import { TRACKED_LANGUAGES, type Implementation, type NewImplementation, type ProjectType } from '../../roadmap'

// Submit form of the project page; see design/ProjectType.dc.html and README → "Project page data".
// No deploy link field until project-service stores deploy links.
const props = defineProps<{
  projectType: ProjectType
  // The first implementation of this project: "Сдать проект" and no cancel button.
  first: boolean
  submit: (input: NewImplementation) => Promise<Implementation>
}>()

const emit = defineEmits<{
  // The user changed something, so the form shouldn't collapse under them.
  edited: []
  submitted: [implementation: Implementation]
  cancel: []
}>()

const OTHER = 'Другой'
const languageOptions = [...TRACKED_LANGUAGES, OTHER]

// Java preselected: the most common choice (the mockup starts with none).
const language = ref<string | null>(languageOptions[0])
const otherLanguage = ref('')
const githubUrl = ref('')

const githubError = ref<string>()
const submitFailed = ref(false)
const submitting = ref(false)

const ids = { otherLanguage: useId(), github: useId(), language: useId() }

// Format is checked on submit; editing the field clears its error.
watch(githubUrl, () => (githubError.value = undefined))

watch([language, otherLanguage, githubUrl], () => emit('edited'), { once: true })

const missing = computed(() => {
  const parts: string[] = []
  if (!language.value) {
    parts.push('выберите язык')
  } else if (language.value === OTHER && !otherLanguage.value.trim()) {
    parts.push('укажите название языка')
  }
  if (!githubUrl.value.trim()) {
    parts.push('укажите ссылку на репозиторий')
  }
  const text = parts.join(' и ')
  return text && text.charAt(0).toUpperCase() + text.slice(1)
})

const GITHUB_REPOSITORY = /^https:\/\/(www\.)?github\.com\/[\w.-]+\/[\w.-]+\/?$/i

async function onSubmit() {
  if (missing.value || submitting.value) {
    return
  }
  const github = githubUrl.value.trim()
  githubError.value = GITHUB_REPOSITORY.test(github)
    ? undefined
    : 'Укажите ссылку вида https://github.com/username/repo'
  if (githubError.value) {
    return
  }

  submitting.value = true
  submitFailed.value = false
  try {
    const implementation = await props.submit({
      language: language.value === OTHER ? otherLanguage.value.trim() : language.value!,
      githubUrl: github,
    })
    emit('submitted', implementation)
  } catch (error) {
    if (error instanceof ConflictError) {
      githubError.value =
        'Этот репозиторий уже зарегистрирован как реализация. Одна ссылка на GitHub — одна реализация: укажите другой репозиторий.'
    } else {
      submitFailed.value = true
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Card>
    <template #content>
      <form class="flex flex-col gap-4" novalidate :aria-busy="submitting" @submit.prevent="onSubmit">
        <div class="flex flex-col gap-0.5">
          <h2 class="text-base/[1.375rem] font-semibold">{{ first ? 'Сдать проект' : 'Новая реализация' }}</h2>
          <p class="text-meta text-muted-color">Ревью не обязательно — проект засчитывается сразу после сдачи</p>
        </div>

        <div class="flex flex-col gap-1.5">
          <span :id="ids.language" class="text-meta font-semibold text-(--p-tint-neutral-color)">Язык</span>
          <SelectButton
            v-model="language"
            :options="languageOptions"
            :allow-empty="false"
            :disabled="submitting"
            :aria-labelledby="ids.language"
            fluid
          />
          <div v-if="language === OTHER" class="flex flex-col gap-1.5 pt-1">
            <label :for="ids.otherLanguage" class="text-meta font-semibold text-(--p-tint-neutral-color)">
              Название языка
            </label>
            <InputText
              :id="ids.otherLanguage"
              v-model="otherLanguage"
              placeholder="Например, Kotlin"
              :disabled="submitting"
              fluid
            />
            <p class="flex gap-1.5 text-note text-muted-color">
              <i class="pi pi-info-circle mt-px shrink-0 text-xs" aria-hidden="true" />
              Реализация сохранится в списке, но не попадёт в прогресс роадмапов — он считается только для
              Java, Python и Go
            </p>
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <label :for="ids.github" class="text-meta font-semibold text-(--p-tint-neutral-color)">
            Ссылка на GitHub-репозиторий
          </label>
          <IconField>
            <InputIcon class="pi pi-link" />
            <InputText
              :id="ids.github"
              v-model="githubUrl"
              type="url"
              inputmode="url"
              autocomplete="off"
              placeholder="https://github.com/username/repo"
              :invalid="Boolean(githubError)"
              :disabled="submitting"
              fluid
            />
          </IconField>
          <Message v-if="githubError" severity="error" size="small" variant="simple" icon="pi pi-exclamation-circle" role="alert">
            {{ githubError }}
          </Message>
          <small v-else class="text-note text-muted-color">Репозиторий должен быть публичным</small>
        </div>

        <Message v-if="submitFailed" severity="error" icon="pi pi-exclamation-circle" role="alert">
          Не удалось сдать проект. Попробуйте ещё раз.
        </Message>

        <div class="flex flex-col gap-1">
          <Button type="submit" label="Сдать проект" size="large" :loading="submitting" :disabled="Boolean(missing)" />
          <p v-if="missing && !submitting" class="pt-0.5 text-center text-note text-muted-color">{{ missing }}</p>
          <Button
            v-if="!first"
            label="Отмена"
            severity="secondary"
            text
            :disabled="submitting"
            @click="emit('cancel')"
          />
        </div>
      </form>
    </template>
  </Card>
</template>
