<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import SelectButton from 'primevue/selectbutton'
import Tag from 'primevue/tag'
import { ApiError, HttpError, NotFoundError } from '../api'
import { authenticateDummy, knownRoles, type Role } from '../session'
import { telegramAppUrl } from '../telegram'

// Dummy login, shown by the app shell instead of any route in a regular browser in test
// environments; see design/DevLogin.dc.html.
defineProps<{
  expired?: boolean
}>()

// Names the environment by Vite mode; the fallback covers a mode added later with dev tools on.
const environmentLabels: Record<string, string> = {
  staging: 'Staging окружение',
  'local-stack': 'Локальное окружение',
}
const environmentLabel = environmentLabels[import.meta.env.MODE] ?? 'Тестовое окружение'

// The last successful values prefill the form, so signing in again after expiry is one click.
const LAST_LOGIN_KEY = 'dev-login-last'
type LastLogin = { userId: number; username: string; roles: Role[] }

function readLastLogin(): Partial<LastLogin> {
  try {
    return JSON.parse(localStorage.getItem(LAST_LOGIN_KEY) ?? '{}') ?? {}
  } catch {
    return {}
  }
}

const lastLogin = readLastLogin()
const userId = ref<number | null>(typeof lastLogin.userId === 'number' ? lastLogin.userId : null)
const username = ref(typeof lastLogin.username === 'string' ? lastLogin.username : '')
const roles = ref<Role[]>(
  Array.isArray(lastLogin.roles) ? lastLogin.roles.filter((role) => knownRoles.includes(role)) : [],
)

const loading = ref(false)
const notFoundId = ref<number>()
const error = ref<string>()

const valid = computed(
  () => (userId.value ?? 0) >= 1 && username.value.trim() !== '' && roles.value.length > 0,
)

// Errors describe the values that were sent; editing any field dismisses them.
watch([userId, username, roles], () => {
  notFoundId.value = undefined
  error.value = undefined
})

function setUsername(value: string | undefined) {
  username.value = (value ?? '').replace(/^@/, '')
}

async function submit() {
  if (!valid.value || loading.value) {
    return
  }
  const login: LastLogin = { userId: userId.value!, username: username.value.trim(), roles: roles.value }
  const id = login.userId
  loading.value = true
  try {
    await authenticateDummy({ user_id: id, roles: login.roles, telegram_username: login.username })
    localStorage.setItem(LAST_LOGIN_KEY, JSON.stringify(login))
  } catch (e) {
    if (e instanceof NotFoundError) {
      notFoundId.value = id
    } else {
      if (!(e instanceof ApiError)) {
        console.error('Unexpected dummy authentication error', e)
      }
      error.value = (e instanceof HttpError && e.body?.message) || 'Сервер недоступен. Попробуйте ещё раз.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- Fills the app shell, whose padding already includes the safe areas. -->
  <div class="flex flex-1 flex-col gap-4">
    <div class="flex flex-1 flex-col gap-4">
      <Message v-if="expired" severity="info" icon="pi pi-clock" role="status">
        <span class="font-semibold">Сессия истекла — войдите снова.</span> Тестовая сессия действует
        30 минут.
      </Message>

      <header class="flex flex-col items-center gap-2.5 text-center">
        <Avatar
          icon="pi pi-code"
          shape="circle"
          class="tint-warn size-14"
          :dt="{ icon: { size: '1.75rem' } }"
          aria-hidden="true"
        />
        <Tag :value="environmentLabel" severity="warn" class="tracking-wide uppercase" />
        <h1 class="text-page font-bold">Вход для разработчиков</h1>
        <p class="max-w-82 text-sm text-muted-color">
          Приложение открыто в браузере. В тестовом окружении можно войти под любым пользователем без
          Telegram.
        </p>
      </header>

      <Card>
        <template #content>
          <form id="dev-login" class="flex flex-col gap-3.5" novalidate @submit.prevent="submit">
            <div class="flex flex-col gap-1.5">
              <label for="dev-login-user-id" class="text-meta font-semibold text-(--p-tint-neutral-color)">
                ID пользователя
              </label>
              <InputNumber
                v-model="userId"
                input-id="dev-login-user-id"
                :min="1"
                :use-grouping="false"
                placeholder="Например, 1"
                :invalid="notFoundId !== undefined"
                :disabled="loading"
                fluid
              />
              <Message
                v-if="notFoundId !== undefined"
                severity="error"
                size="small"
                variant="simple"
                icon="pi pi-exclamation-circle"
                role="alert"
              >
                Пользователь с ID {{ notFoundId }} не найден
              </Message>
              <small class="text-note text-muted-color">ID из таблицы users в auth-service — не Telegram ID</small>
            </div>

            <div class="flex flex-col gap-1.5">
              <label for="dev-login-username" class="text-meta font-semibold text-(--p-tint-neutral-color)">
                Telegram username
              </label>
              <InputGroup>
                <InputGroupAddon aria-hidden="true">@</InputGroupAddon>
                <InputText
                  id="dev-login-username"
                  :model-value="username"
                  placeholder="username"
                  autocomplete="off"
                  autocapitalize="off"
                  spellcheck="false"
                  :disabled="loading"
                  @update:model-value="setUsername"
                />
              </InputGroup>
            </div>

            <div class="flex flex-col gap-1.5">
              <span id="dev-login-roles" class="text-meta font-semibold text-(--p-tint-neutral-color)">Роли</span>
              <SelectButton
                v-model="roles"
                :options="knownRoles"
                multiple
                :disabled="loading"
                aria-labelledby="dev-login-roles"
                fluid
              >
                <template #option="{ option }">
                  <span class="inline-flex items-center gap-1 text-xs font-bold tracking-wide">
                    <i v-if="roles.includes(option)" class="pi pi-check text-[0.6875rem]" aria-hidden="true" />
                    {{ option }}
                  </span>
                </template>
              </SelectButton>
              <small class="text-note text-muted-color">
                Сессия получит эти роли независимо от настоящих ролей пользователя. Нужна хотя бы одна.
              </small>
            </div>
          </form>
        </template>
      </Card>
    </div>

    <div class="flex flex-col gap-2">
      <Message v-if="error" severity="error" icon="pi pi-exclamation-circle" role="alert">
        {{ error }}
      </Message>
      <Button
        type="submit"
        form="dev-login"
        :label="loading ? 'Входим…' : 'Войти'"
        :loading="loading"
        :disabled="!valid"
        size="large"
      />
      <Button as="a" :href="telegramAppUrl" label="Открыть в Telegram" text />
    </div>
  </div>
</template>
