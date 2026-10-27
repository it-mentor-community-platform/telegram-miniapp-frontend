// Request body of POST /api/auth/by-telegram (auth-service `TelegramAuthRequestDto`).
export type TelegramAuthRequestDto = {
  // Telegram.WebApp.initData as is, still URL-encoded.
  initDataRaw: string
}

// Request body of POST /api/auth/by-dummy (auth-service `DummyRequestDto`). Exists in test
// environments only.
export type DummyAuthRequestDto = {
  // Users.id in auth-service, not the Telegram id.
  user_id: number
  // Any known roles, whatever the user's real ones; at least one.
  roles: string[]
  // Without "@".
  telegram_username: string
}
