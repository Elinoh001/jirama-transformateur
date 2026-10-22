import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

// Pinia doit être installé avant le router (les guards utilisent les stores).
app.use(createPinia())
app.use(router)

app.mount('#app')