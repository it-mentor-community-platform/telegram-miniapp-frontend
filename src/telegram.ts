import type { Router } from 'vue-router'
import { parentLocation } from './composables/useBreadcrumbs'

// telegram-web-app.js defines WebApp in any browser; outside Telegram its platform is 'unknown'.
const telegram =
  window.Telegram?.WebApp.platform !== 'unknown' ? window.Telegram?.WebApp : undefined

export const isTelegram = Boolean(telegram)

// Empty outside Telegram: the app can't authenticate there and shows the auth error screen.
export const initData = telegram?.initData ?? ''

export const telegramUser = telegram?.initDataUnsafe.user

export function initTelegram() {
  if (telegram) {
    applyColorScheme(telegram.colorScheme === 'dark')
    telegram.onEvent?.('themeChanged', () => applyColorScheme(telegram.colorScheme === 'dark'))
    telegram.ready()
    telegram.expand?.()
    return
  }

  const media = window.matchMedia('(prefers-color-scheme: dark)')
  applyColorScheme(media.matches)
  media.addEventListener('change', (event) => applyColorScheme(event.matches))
}

export function closeApp() {
  telegram?.close()
}

// Telegram's BackButton replaces in-app back navigation: hidden on home, elsewhere it leads to the
// breadcrumb parent rather than browser history, so deep-linked screens still have somewhere to go.
export function bindBackButton(router: Router) {
  const backButton = telegram?.BackButton
  if (!backButton) {
    return
  }

  backButton.onClick(() => router.push(parentLocation(router.currentRoute.value)))
  router.afterEach((to) => {
    if (to.name === 'home') {
      backButton.hide()
    } else {
      backButton.show()
    }
  })
}

function applyColorScheme(dark: boolean) {
  document.documentElement.classList.toggle('app-dark', dark)
}
