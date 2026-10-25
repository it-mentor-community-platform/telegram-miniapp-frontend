// Request body of POST /api/auth/by-telegram (auth-service `TelegramAuthRequestDto`).
export type TelegramAuthRequestDto = {
  // Telegram.WebApp.initData as is, still URL-encoded.
  initDataRaw: string
}
