import { reactive } from 'vue'
import {
  ApiError,
  authenticateByDummy,
  authenticateByTelegram,
  setAccessTokenProvider,
  setUnauthorizedHandler,
  type AccessToken,
  type DummyAuthRequestDto,
} from './api'
import { initData, telegramUser } from './telegram'

export type Role = 'STUDENT' | 'MENTOR' | 'ADMIN'

export type CurrentUser = {
  telegramUserId: string
  firstName: string
  lastName?: string
  roles: Role[]
}

export type SessionStatus =
  | 'pending'
  | 'authenticated'
  | 'outside-telegram'
  | 'failed'
  | 'expired'
  // Test environments in a regular browser: the dummy login form, fresh or after its session expired.
  | 'dummy-login'
  | 'dummy-expired'

export const knownRoles: Role[] = ['STUDENT', 'MENTOR', 'ADMIN']

// Test environments (local-stack, staging) only; auth-service has no dummy login in prod.
export const dummyAuthEnabled = import.meta.env.VITE_SHOW_DEV_TOOLS === 'true'

export const session = reactive<{ status: SessionStatus; user: CurrentUser | null }>({
  status: 'pending',
  user: null,
})

// Kept in memory only: every Mini App launch brings fresh init data to authenticate with.
let accessToken: string | undefined
setAccessTokenProvider(() => accessToken)

// The init data expires along with the token, so re-authenticating can't help: only a relaunch can.
// Outside Telegram the session came from the dummy login, which can simply be repeated.
setUnauthorizedHandler(() => {
  accessToken = undefined
  session.status = initData ? 'expired' : 'dummy-expired'
})

let resolveAuthenticated: () => void
// Resolves on the first successful authentication. Until then the router holds the initial
// navigation, so the URL is kept and the target page opens once a retry succeeds.
export const whenAuthenticated = new Promise<void>((resolve) => (resolveAuthenticated = resolve))

export async function authenticate() {
  if (!initData) {
    session.status = dummyAuthEnabled ? 'dummy-login' : 'outside-telegram'
    return
  }

  // A retry keeps the 'failed' status: the error screen shows its own loading state meanwhile.
  try {
    signIn(await authenticateByTelegram(initData))
  } catch (error) {
    // ApiError covers rejected init data and an unreachable backend; anything else is a bug, but
    // still leaves the user on the retry screen rather than a spinner.
    if (!(error instanceof ApiError)) {
      console.error('Unexpected authentication error', error)
    }
    session.status = 'failed'
  }
}

// Rejects with the ApiError for the dummy login form to show; the status stays unchanged.
export async function authenticateDummy(request: DummyAuthRequestDto) {
  signIn(await authenticateByDummy(request))
}

function signIn(token: AccessToken) {
  accessToken = token.raw
  session.user = {
    telegramUserId: token.claims.sub,
    // The token carries no name; Telegram's copy is trusted now that the backend accepted it.
    firstName: telegramUser?.first_name ?? '',
    lastName: telegramUser?.last_name,
    roles: token.claims.roles.filter((role): role is Role => knownRoles.includes(role as Role)),
  }
  session.status = 'authenticated'
  resolveAuthenticated()
}
