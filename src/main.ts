import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import 'primeicons/primeicons.css'

import App from './App.vue'
import { router } from './router'
import { authenticate } from './session'
import { bindBackButton, initTelegram } from './telegram'
import { AppPreset } from './theme'
import './styles.css'

initTelegram()
// Not awaited: the app shell shows a spinner, then the routes or an auth error screen.
authenticate()

const app = createApp(App)

app.use(PrimeVue, {
  theme: {
    preset: AppPreset,
    options: {
      darkModeSelector: '.app-dark',
    },
  },
})
app.use(router)
bindBackButton(router)

app.mount('#app')
