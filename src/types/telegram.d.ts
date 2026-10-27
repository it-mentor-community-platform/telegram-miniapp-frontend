interface TelegramBackButton {
  show: () => void
  hide: () => void
  onClick: (callback: () => void) => void
  offClick: (callback: () => void) => void
}

// Unverified copy of the init data's `user` field; trusted once the backend accepts the init data.
interface TelegramWebAppUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
}

interface TelegramWebApp {
  initData: string
  initDataUnsafe: {
    user?: TelegramWebAppUser
  }
  platform: string
  colorScheme?: 'light' | 'dark'
  BackButton?: TelegramBackButton
  ready: () => void
  close: () => void
  expand?: () => void
  onEvent?: (eventType: 'themeChanged', callback: () => void) => void
  offEvent?: (eventType: 'themeChanged', callback: () => void) => void
}

interface Window {
  Telegram?: {
    WebApp: TelegramWebApp
  }
}
