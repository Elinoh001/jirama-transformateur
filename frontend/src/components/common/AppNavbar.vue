<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Bell, ChevronDown, LogOut, Menu, Search, User } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/authStore'
import { useDashboardStore } from '@/stores/dashboardStore'

const emit = defineEmits(['toggle-sidebar'])

const auth = useAuthStore()
const dashboard = useDashboardStore()
const route = useRoute()
const router = useRouter()

// Horloge du navigateur, mise à jour chaque minute.
const maintenant = ref(new Date())
let timer = null
onMounted(() => {
  timer = setInterval(() => {
    maintenant.value = new Date()
  }, 30_000)
  document.addEventListener('click', handleClickOutside)
})
onBeforeUnmount(() => {
  clearInterval(timer)
  document.removeEventListener('click', handleClickOutside)
})

const dateTexte = computed(() => {
  const texte = maintenant.value.toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
  return texte.charAt(0).toUpperCase() + texte.slice(1)
})
const heureTexte = computed(() =>
  maintenant.value.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
)

function deconnecter() {
  auth.logout()
  dashboard.reset()
  router.push({ name: 'login' })
}

// --- Gestion du menu profil ---
const showProfileMenu = ref(false)
const profileMenuRef = ref(null)

function handleClickOutside(event) {
  if (profileMenuRef.value && !profileMenuRef.value.contains(event.target)) {
    showProfileMenu.value = false
  }
}
</script>

<template>
  <header class="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 shadow-sm sm:px-6">
    
    <!-- PARTIE GAUCHE : Menu mobile + Recherche + Titre -->
    <div class="flex flex-1 items-center gap-4">
      <!-- Bouton menu mobile -->
      <button
        type="button"
        class="cursor-pointer rounded-lg p-2 text-slate-700 hover:bg-slate-100 lg:hidden"
        aria-label="Ouvrir le menu"
        @click="emit('toggle-sidebar')"
      >
        <Menu class="h-5 w-5" />
      </button>

      <!-- Barre de recherche -->
      <div class="relative w-full max-w-sm">
        <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Rechercher un transformateur..."
          class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-4 text-sm text-slate-700 outline-none transition-colors focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100"
        />
      </div>

      <!-- Titre de la page (optionnel, sur écrans larges) -->
      <h1 class="hidden truncate text-lg font-bold text-slate-800 xl:block">
        {{ route.meta.title }}
      </h1>
    </div>

    <!-- PARTIE DROITE : Horloge, Notifs, Profil, Déconnexion -->
    <div class="flex items-center gap-2 sm:gap-3">
      
      <!-- Horloge -->
      <div class="hidden items-center gap-3 rounded-lg border border-slate-200 px-3 py-1.5 text-xs lg:flex">
        <span class="text-slate-600">{{ dateTexte }}</span>
        <span class="border-l border-slate-200 pl-3 font-semibold text-slate-900">{{ heureTexte }}</span>
      </div>

      <!-- Notifications -->
      <button class="relative cursor-pointer rounded-lg p-2 text-slate-600 transition-colors hover:bg-slate-100">
        <Bell class="h-5 w-5" />
        <span class="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
      </button>

      <!-- Séparateur -->
      <div class="h-8 w-px bg-slate-200"></div>

      <!-- Menu Profil -->
      <div class="relative" ref="profileMenuRef">
        <button
          type="button"
          class="flex cursor-pointer items-center gap-2 rounded-lg p-1.5 pr-2 transition-colors hover:bg-slate-100"
          @click="showProfileMenu = !showProfileMenu"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white">
            <User class="h-4 w-4" />
          </div>
          <span class="hidden text-sm font-semibold text-slate-700 sm:block">
            {{ auth.fullName || 'Admin' }}
          </span>
          <ChevronDown class="h-4 w-4 text-slate-400" />
        </button>

        <!-- Menu déroulant -->
        <div
          v-if="showProfileMenu"
          class="absolute right-0 top-12 w-48 overflow-hidden rounded-lg border border-slate-200 bg-white py-1 shadow-lg z-50"
        >
          <RouterLink
            to="/profil"
            class="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
            @click="showProfileMenu = false"
          >
            Mon profil
          </RouterLink>
          <RouterLink
            to="/parametres"
            class="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
            @click="showProfileMenu = false"
          >
            Paramètres
          </RouterLink>
          <div class="my-1 border-t border-slate-100"></div>
          <button
            @click="deconnecter(); showProfileMenu = false;"
            class="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50"
          >
            <LogOut class="h-4 w-4" />
            Déconnexion
          </button>
        </div>
      </div>

      <!-- Bouton Déconnexion (visible sur écrans larges uniquement) -->
      <button
        type="button"
        class="hidden cursor-pointer items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:border-red-300 hover:bg-red-50 hover:text-red-700 xl:flex"
        @click="deconnecter"
      >
        <LogOut class="h-4 w-4" />
        <span>Déconnexion</span>
      </button>
    </div>
  </header>
</template>