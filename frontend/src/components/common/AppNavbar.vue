<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { LogOut, Menu } from 'lucide-vue-next'
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
})
onBeforeUnmount(() => clearInterval(timer))

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
</script>

<template>
  <header class="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 shadow-sm sm:px-6">
    <div class="flex min-w-0 items-center gap-3">
      <button
        type="button"
        class="cursor-pointer rounded-lg p-2 text-navy-800 hover:bg-slate-100 lg:hidden"
        aria-label="Ouvrir le menu"
        @click="emit('toggle-sidebar')"
      >
        <Menu class="h-6 w-6" />
      </button>
      <h1 class="truncate text-lg font-bold text-navy-900">{{ route.meta.title }}</h1>
    </div>

    <div class="flex items-center gap-3 sm:gap-5">
      <div class="hidden items-center gap-3 rounded-lg border border-slate-200 px-3 py-1.5 text-sm md:flex">
        <span class="text-slate-600">{{ dateTexte }}</span>
        <span class="border-l border-slate-200 pl-3 font-semibold text-navy-900">{{ heureTexte }}</span>
      </div>

      <div class="hidden text-right leading-tight sm:block">
        <p class="text-sm font-semibold text-navy-900">{{ auth.fullName }}</p>
      </div>

      <button
        type="button"
        class="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
        @click="deconnecter"
      >
        <LogOut class="h-4 w-4" />
        <span class="hidden sm:inline">Déconnexion</span>
      </button>
    </div>
  </header>
</template>