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
import { ApiError, BadRequestError, HttpError, NotFoundError, type DummyAuthUserLookupDto } from '../api'
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

// The user is looked up by exactly one of these; each maps to its by-dummy request field.
type Method = 'id' | 'telegram' | 'github'
const methodOptions: { value: Method; label: string }[] = [
  { value: 'id', label: 'Telegram ID' },
  { value: 'telegram', label: 'Telegram' },
  { value: 'github', label: 'GitHub' },
]
const methods = methodOptions.map((option) => option.value)

type LinkMethod = Exclude<Method, 'id'>

// Only the username is typed after a fixed prefix; the link is built from it when sending.
const linkPrefixes: Record<LinkMethod, string> = { telegram: 't.me/', github: 'github.com/' }
const linkLabels: Record<LinkMethod, string> = { telegram: 'Username в Telegram', github: 'Username на GitHub' }
const hints: Record<Method, string> = {
  id: 'Числовой ID аккаунта Telegram (telegram_user_id), не ID из базы',
  telegram: 'Username из профиля участника. Можно вставить ссылку или @username',
  github: 'Username из профиля участника. Можно вставить ссылку целиком',
}
const formatErrors: Record<LinkMethod, string> = {
  telegram: 'Только username — латинские буквы, цифры и _',
  github: 'Только username — латинские буквы, цифры и дефис',
}

// A pasted link or @username is cut down to the username as it's entered.
const LINK_PREFIXES: Record<LinkMethod, RegExp> = {
  telegram: /^\s*(?:@|(?:https?:\/\/)?t\.me\/)/,
  github: /^\s*(?:https?:\/\/)?(?:www\.)?github\.com\//,
}
// profile-service has the final say on the format; this only catches obvious typos before sending.
const USERNAMES: Record<LinkMethod, RegExp> = {
  telegram: /^[A-Za-z0-9_]{4,32}$/,
  github: /^[A-Za-z0-9-]+$/,
}

function toUsername(method: LinkMethod, value: string): string {
  return value.replace(LINK_PREFIXES[method], '').trim()
}

// The last successful values prefill the form, so signing in again after expiry is one click.
const LAST_LOGIN_KEY = 'dev-login-last'
type LastLogin = { method: Method; value: string; roles: Role[] }

function readLastLogin(): Partial<LastLogin> {
  try {
    return JSON.parse(localStorage.getItem(LAST_LOGIN_KEY) ?? '{}') ?? {}
  } catch {
    return {}
  }
}

const lastLogin = readLastLogin()
const lastMethod = methods.includes(lastLogin.method as Method) ? (lastLogin.method as Method) : undefined
const method = ref<Method>(lastMethod ?? 'telegram')
const telegramId = ref<number | null>(lastMethod === 'id' && /^[1-9][0-9]*$/.test(String(lastLogin.value)) ? Number(lastLogin.value) : null)
const usernames = ref<Record<LinkMethod, string>>({
  telegram: lastMethod === 'telegram' && typeof lastLogin.value === 'string' ? toUsername('telegram', lastLogin.value) : '',
  github: lastMethod === 'github' && typeof lastLogin.value === 'string' ? toUsername('github', lastLogin.value) : '',
})

function setUsername(method: LinkMethod, value: string | undefined) {
  usernames.value[method] = toUsername(method, value ?? '')
}
const roles = ref<Role[]>(
  Array.isArray(lastLogin.roles) ? lastLogin.roles.filter((role) => knownRoles.includes(role)) : [],
)

const loading = ref(false)
const fieldError = ref<string>()
const error = ref<string>()

const filled = computed(
  () =>
    (method.value === 'id' ? (telegramId.value ?? 0) >= 1 : usernames.value[method.value] !== '') &&
    roles.value.length > 0,
)

// Errors describe the values that were sent; editing any field dismisses them.
watch([method, telegramId, usernames, roles], () => {
  fieldError.value = undefined
  error.value = undefined
}, { deep: true })

// The lookup field for the request, or undefined when the username has the wrong format.
function userLookup(): { lookup: DummyAuthUserLookupDto; value: string; shown: string } | undefined {
  if (method.value === 'id') {
    const id = telegramId.value!
    return { lookup: { telegram_user_id: id }, value: String(id), shown: `Telegram ID ${id}` }
  }
  const username = usernames.value[method.value].replace(/\/$/, '')
  if (!USERNAMES[method.value].test(username)) {
    return undefined
  }
  const shown = linkPrefixes[method.value] + username
  const link = `https://${shown}`
  const lookup = method.value === 'telegram' ? { telegram_url: link } : { github_profile_url: link }
  return { lookup, value: username, shown }
}

async function submit() {
  if (!filled.value || loading.value) {
    return
  }
  const user = userLookup()
  if (!user) {
    fieldError.value = formatErrors[method.value as LinkMethod]
    return
  }
  const login: LastLogin = { method: method.value, value: user.value, roles: roles.value }
  loading.value = true
  try {
    await authenticateDummy({ ...user.lookup, roles: login.roles })
    localStorage.setItem(LAST_LOGIN_KEY, JSON.stringify(login))
  } catch (e) {
    if (e instanceof NotFoundError) {
      fieldError.value =
        method.value === 'id' ? `Пользователь с ${user.shown} не найден` : `Профиль со ссылкой ${user.shown} не найден`
    } else if (e instanceof BadRequestError && method.value !== 'id') {
      // profile-service rejected the link format (its message is technical, so ours is shown);
      // roles come from a fixed list and are always known.
      fieldError.value = formatErrors[method.value]
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
              <span id="dev-login-user" class="text-meta font-semibold text-(--p-tint-neutral-color)">Пользователь</span>
              <SelectButton
                v-model="method"
                :options="methodOptions"
                option-label="label"
                option-value="value"
                :allow-empty="false"
                :disabled="loading"
                aria-labelledby="dev-login-user"
                :pt="{ pcToggleButton: { content: { class: 'px-2' } } }"
                fluid
              >
                <!-- Mockup's 13 px semibold labels and narrower padding keep «Telegram ID» on one line in a third of the card. -->
                <template #option="{ option }">
                  <span class="text-meta font-semibold whitespace-nowrap">{{ option.label }}</span>
                </template>
              </SelectButton>
              <InputNumber
                v-if="method === 'id'"
                v-model="telegramId"
                input-id="dev-login-value"
                :min="1"
                :use-grouping="false"
                placeholder="Например, 123456789"
                aria-label="Telegram ID пользователя"
                :invalid="fieldError !== undefined"
                :disabled="loading"
                class="mt-0.5"
                fluid
              />
              <InputGroup v-else class="mt-0.5">
                <InputGroupAddon aria-hidden="true">{{ linkPrefixes[method] }}</InputGroupAddon>
                <InputText
                  id="dev-login-value"
                  :model-value="usernames[method]"
                  placeholder="username"
                  :aria-label="linkLabels[method]"
                  autocomplete="off"
                  autocapitalize="off"
                  spellcheck="false"
                  :invalid="fieldError !== undefined"
                  :disabled="loading"
                  @update:model-value="setUsername(method, $event)"
                />
              </InputGroup>
              <Message
                v-if="fieldError"
                severity="error"
                size="small"
                variant="simple"
                icon="pi pi-exclamation-circle"
                role="alert"
              >
                {{ fieldError }}
              </Message>
              <small class="text-note text-muted-color">{{ hints[method] }}</small>
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
        :disabled="!filled"
        size="large"
      />
      <Button as="a" :href="telegramAppUrl" label="Открыть в Telegram" text />
    </div>
  </div>
</template>
