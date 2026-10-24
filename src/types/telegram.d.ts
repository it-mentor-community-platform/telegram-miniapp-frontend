interface TelegramBackButton {
  show: () => void
  hide: () => void
  onClick: (callback: () => void) => void
  offClick: (callback: () => void) => void
}

interface TelegramWebApp {
  initData: string
  platform: string
  colorScheme?: 'light' | 'dark'
  BackButton?: TelegramBackButton
  ready: () => void
  expand?: () => void
  onEvent?: (eventType: 'themeChanged', callback: () => void) => void
  offEvent?: (eventType: 'themeChanged', callback: () => void) => void
}

interface Window {
  Telegram?: {
    WebApp: TelegramWebApp
  }
}
