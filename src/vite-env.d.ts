/// <reference types="vite/client" />

// Per-environment values live in .env.<mode> (local-stack | staging | prod).
interface ImportMetaEnv {
  // Gateway root the API is called on, e.g. "https://staging.platform.zhukovsd.it".
  readonly VITE_API_BASE_URL: string
  // Bot whose Mini App this build is, without "@". Used for "Открыть в Telegram" links.
  readonly VITE_TELEGRAM_BOT_USERNAME: string
  // "true" shows developer tools (home "Для разработчиков" panel). Never in prod.
  readonly VITE_SHOW_DEV_TOOLS?: string
  // Mocked project implementations: empty | java3 | multi | java6 | other. Defaults to "multi".
  readonly VITE_MOCK_PROJECTS?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
