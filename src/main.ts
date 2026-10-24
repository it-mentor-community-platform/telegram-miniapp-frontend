import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import 'primeicons/primeicons.css'

import App from './App.vue'
import { router } from './router'
import { bindBackButton, initTelegram } from './telegram'
import { AppPreset } from './theme'
import './styles.css'

initTelegram()

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
