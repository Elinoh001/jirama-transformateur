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
const anneeCourante = new Date().getFullYear()

// Comptes de DÉVELOPPEMENT : disponibles uniquement avec « npm run dev ».
// Dans la version de production (npm run build), la liste est vide : aucun mot de passe n'est embarqué.
const COMPTES_DEMO = import.meta.env.DEV
  ? [
      { label: 'Admin', email: 'admin@jirama.local', password: 'Admin123!' },
      { label: 'Superviseur', email: 'superviseur@jirama.local', password: 'Superviseur123!' },
      { label: 'Agent', email: 'agent@jirama.local', password: 'Agent123!' },
    ]
  : []

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
    <div class="relative hidden w-1/2 bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 lg:block">
      
      <!-- L'IMAGE DU DÉBUT EST DE RETOUR, MAIS SANS FILTRE SOMBRE POUR QU'ELLE SOIT NETTE -->
      <img 
        src="https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?q=80&w=2070&auto=format&fit=crop" 
        alt="Lignes électriques JIRAMA" 
        class="absolute inset-0 h-full w-full object-cover"
        @error="$event.target.style.display = 'none'"
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

          <!-- Mot de passe oublié : la réinitialisation passe par un administrateur -->
          <p class="text-sm text-slate-500">
            Mot de passe oublié ? Contactez un administrateur.
          </p>

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

        <!-- Footer Copyright -->
        <p class="mt-10 text-center text-xs text-slate-400">
          © {{ anneeCourante }} JIRAMA. Tous droits réservés.
        </p>

        <!-- Comptes de développement -->
        <div v-if="COMPTES_DEMO.length" class="mt-8 border-t border-slate-100 pt-4 opacity-50 hover:opacity-100 transition-opacity">
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