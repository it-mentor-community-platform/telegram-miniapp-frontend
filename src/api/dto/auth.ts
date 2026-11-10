// Request body of POST /api/auth/by-telegram (auth-service `TelegramAuthRequestDto`).
export type TelegramAuthRequestDto = {
  // Telegram.WebApp.initData as is, still URL-encoded.
  initDataRaw: string
}

// Request body of POST /api/auth/by-dummy (auth-service `DummyRequestDto`). Exists in test
// environments only. Exactly one lookup field identifies the user.
export type DummyAuthRequestDto = DummyAuthUserLookupDto & {
  // Any known roles, whatever the user's real ones; at least one.
  roles: string[]
}

export type DummyAuthUserLookupDto =
  // Users.telegram_user_id in auth-service.
  | { telegram_user_id: number }
  // Profile's Telegram link, https://t.me/<username>; profile-service checks the format.
  | { telegram_url: string }
  // Profile's GitHub account link, https://github.com/<username>; profile-service checks the format.
  | { github_profile_url: string }
