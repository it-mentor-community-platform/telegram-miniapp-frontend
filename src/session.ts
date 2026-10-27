import { reactive } from 'vue'
import {
  ApiError,
  authenticateByTelegram,
  setAccessTokenProvider,
  setUnauthorizedHandler,
} from './api'
import { initData, telegramUser } from './telegram'

export type Role = 'STUDENT' | 'MENTOR' | 'ADMIN'

export type CurrentUser = {
  telegramUserId: string
  firstName: string
  lastName?: string
  roles: Role[]
}

export type SessionStatus = 'pending' | 'authenticated' | 'outside-telegram' | 'failed' | 'expired'

const knownRoles: Role[] = ['STUDENT', 'MENTOR', 'ADMIN']

export const session = reactive<{ status: SessionStatus; user: CurrentUser | null }>({
  status: 'pending',
  user: null,
})

// Kept in memory only: every Mini App launch brings fresh init data to authenticate with.
let accessToken: string | undefined
setAccessTokenProvider(() => accessToken)

// The init data expires along with the token, so re-authenticating can't help: only a relaunch can.
setUnauthorizedHandler(() => {
  accessToken = undefined
  session.status = 'expired'
})

let resolveAuthenticated: () => void
// Resolves on the first successful authentication. Until then the router holds the initial
// navigation, so the URL is kept and the target page opens once a retry succeeds.
export const whenAuthenticated = new Promise<void>((resolve) => (resolveAuthenticated = resolve))

export async function authenticate() {
  if (!initData) {
    session.status = 'outside-telegram'
    return
  }

  // A retry keeps the 'failed' status: the error screen shows its own loading state meanwhile.
  try {
    const token = await authenticateByTelegram(initData)
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
  } catch (error) {
    // ApiError covers rejected init data and an unreachable backend; anything else is a bug, but
    // still leaves the user on the retry screen rather than a spinner.
    if (!(error instanceof ApiError)) {
      console.error('Unexpected authentication error', error)
    }
    session.status = 'failed'
  }
}
