import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Import Tailwind CSS
import './assets/styles/main.css'

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)

// Mount app
app.mount('#app')

// Register service worker for PWA
if ('serviceWorker' in navigator) {
  import('./utils/pwa').then(({ registerSW }) => {
    registerSW()
  })
}