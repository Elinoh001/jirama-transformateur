<script setup>
import { ref } from 'vue'
import { Eye, EyeOff, Zap, User, Lock, ArrowRight, ShieldCheck } from 'lucide-vue-next'
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
const rememberMe = ref(false)

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
    error.value = getErrorMessage(e, 'Identifiant ou mot de passe incorrect')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen w-full bg-white">
    <!-- Côté Gauche : Image immersive (Masqué sur mobile) -->
    <div class="relative hidden w-1/2 lg:block">
      
      <!-- L'IMAGE DU DÉBUT EST DE RETOUR, MAIS SANS FILTRE SOMBRE POUR QU'ELLE SOIT NETTE -->
      <img 
        src="https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?q=80&w=2070&auto=format&fit=crop" 
        alt="Lignes électriques JIRAMA" 
        class="absolute inset-0 h-full w-full object-cover"
      />
      
      <!-- Dégradé uniquement en bas pour que le texte blanc soit lisible -->
      <div class="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-900/20 to-transparent"></div>

      <!-- Logo en haut -->
      <div class="absolute top-10 left-10 z-10 flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white shadow-lg">
          <Zap class="h-6 w-6" />
        </div>
        <span class="text-xl font-bold text-white drop-shadow-md tracking-wide">JIRAMA Transformateurs</span>
      </div>

      <!-- Texte en bas -->
      <div class="absolute bottom-0 left-0 z-10 p-10 mb-6">
        <h2 class="text-3xl font-bold text-white mb-3 leading-tight drop-shadow-lg">
          Ensemble pour une<br />énergie fiable et durable.
        </h2>
        <p class="text-slate-200 text-sm max-w-md drop-shadow-md">
          Plateforme de gestion, de suivi préventif et de maintenance du parc de transformateurs de la JIRAMA Antsirabe.
        </p>
      </div>
    </div>

    <!-- Côté Droit : Formulaire de connexion -->
    <div class="flex w-full flex-col justify-center px-6 py-12 lg:w-1/2 sm:px-12 lg:px-24 xl:px-32">
      <div class="mx-auto w-full max-w-sm">
        
        <!-- En-tête du formulaire -->
        <div class="mb-8">
          <h1 class="text-2xl font-bold text-slate-900">Connexion</h1>
          <p class="mt-1.5 text-sm text-slate-500">Accédez à votre espace de gestion</p>
        </div>

        <form class="space-y-5" @submit.prevent="submit">
          <!-- Champ Identifiant -->
          <div>
            <label for="email" class="mb-1.5 block text-sm font-medium text-slate-700">Identifiant ou email</label>
            <div class="relative">
              <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <User class="h-5 w-5 text-slate-400" />
              </div>
              <input
                id="email"
                v-model="email"
                type="email"
                required
                autocomplete="username"
                placeholder="nom@jirama.local"
                class="block w-full rounded-lg border border-slate-300 py-2.5 pl-10 pr-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>
          </div>

          <!-- Champ Mot de passe -->
          <div>
            <label for="password" class="mb-1.5 block text-sm font-medium text-slate-700">Mot de passe</label>
            <div class="relative">
              <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <Lock class="h-5 w-5 text-slate-400" />
              </div>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="••••••••"
                class="block w-full rounded-lg border border-slate-300 py-2.5 pl-10 pr-10 text-sm text-slate-900 placeholder-slate-400 outline-none transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 flex cursor-pointer items-center pr-3 text-slate-400 hover:text-slate-600"
                @click="showPassword = !showPassword"
              >
                <EyeOff v-if="showPassword" class="h-5 w-5" />
                <Eye v-else class="h-5 w-5" />
              </button>
            </div>
          </div>

          <!-- Options (Se souvenir / Mot de passe oublié) -->
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="rememberMe"
                type="checkbox"
                class="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
              <label for="remember-me" class="ml-2 block text-sm text-slate-600 cursor-pointer">
                Se souvenir de moi
              </label>
            </div>
            <a href="#" class="text-sm font-medium text-blue-600 hover:text-blue-700">
              Mot de passe oublié ?
            </a>
          </div>

          <!-- Message d'erreur -->
          <div v-if="error" class="rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-100 flex items-center gap-2">
            <ShieldCheck class="h-4 w-4 flex-shrink-0" />
            <p>{{ error }}</p>
          </div>

          <!-- Bouton Se connecter -->
          <button
            type="submit"
            :disabled="loading"
            class="group flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70"
          >
            <span>{{ loading ? 'Connexion en cours...' : 'Se connecter' }}</span>
            <ArrowRight v-if="!loading" class="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </button>
        </form>

        <!-- SSO -->
        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-slate-200"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="bg-white px-2 text-slate-500">Ou se connecter avec</span>
            </div>
          </div>

          <div class="mt-6">
            <button
              type="button"
              class="flex w-full items-center justify-center gap-3 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-200 focus:ring-offset-2"
            >
              <svg class="h-5 w-5" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              S'identifier avec SSO
            </button>
          </div>
        </div>

        <!-- Footer Copyright -->
        <p class="mt-10 text-center text-xs text-slate-400">
          © 2025 JIRAMA. Tous droits réservés.
        </p>

        <!-- Comptes de développement -->
        <div class="mt-8 border-t border-slate-100 pt-4 opacity-50 hover:opacity-100 transition-opacity">
          <p class="mb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400 text-center">
            Mode Développement
          </p>
          <div class="flex justify-center gap-2">
            <button
              v-for="compte in COMPTES_DEMO"
              :key="compte.email"
              type="button"
              class="cursor-pointer rounded border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-500 hover:bg-slate-100 hover:text-slate-700"
              @click="remplir(compte)"
            >
              {{ compte.label }}
            </button>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>