<script setup>
import { ref } from 'vue'
import { Eye, EyeOff, Zap } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'

import { getErrorMessage } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

// Comptes de DÉVELOPPEMENT : à retirer en production.
const COMPTES_DEMO = [
  { label: 'Admin', email: 'admin@jirama.local', password: 'Admin123!' },
  { label: 'Superviseur', email: 'superviseur@jirama.local', password: 'Superviseur123!' },
  { label: 'Agent', email: 'agent@jirama.local', password: 'Agent123!' },
]

function remplir(compte) {
  email.value = compte.email
  password.value = compte.password
  error.value = ''
}

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value.trim(), password.value)
    const redirect =
      typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
        ? route.query.redirect
        : '/dashboard'
    await router.push(redirect)
  } catch (e) {
    error.value = getErrorMessage(e, 'Connexion impossible')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-md">
    <div class="mb-6 text-center">
      <div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-yellow-400 text-slate-900 shadow-lg">
        <Zap class="h-8 w-8" />
      </div>
      <h1 class="text-2xl font-bold text-white">JIRAMA Antsirabe</h1>
      <p class="mt-1 text-sm text-slate-300">Suivi préventif des transformateurs</p>
    </div>

    <div class="rounded-2xl bg-white p-6 shadow-xl sm:p-8">
      <h2 class="mb-5 text-lg font-semibold text-slate-800">Connexion</h2>

      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label for="email" class="mb-1 block text-sm font-medium text-slate-700">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            autocomplete="username"
            placeholder="nom@jirama.local"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          />
        </div>

        <div>
          <label for="password" class="mb-1 block text-sm font-medium text-slate-700">Mot de passe</label>
          <div class="relative">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              autocomplete="current-password"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 flex cursor-pointer items-center px-3 text-slate-500 hover:text-slate-700"
              :aria-label="showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'"
              @click="showPassword = !showPassword"
            >
              <EyeOff v-if="showPassword" class="h-4 w-4" />
              <Eye v-else class="h-4 w-4" />
            </button>
          </div>
        </div>

        <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full cursor-pointer rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>

      <div class="mt-6 border-t border-slate-200 pt-4">
        <p class="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
          Comptes de développement
        </p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="compte in COMPTES_DEMO"
            :key="compte.email"
            type="button"
            class="cursor-pointer rounded-md border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
            @click="remplir(compte)"
          >
            {{ compte.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>