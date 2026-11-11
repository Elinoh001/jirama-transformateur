<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  ClipboardCheck,
  Gauge,
  LayoutDashboard,
  Map,
  ShieldAlert,
  Users,
  Wrench,
  Zap,
  LogOut,
  X,
} from 'lucide-vue-next'

import { useAuthStore } from '@/stores/authStore'
import { ROLE_LABELS } from '@/utils/format'

const props = defineProps({
  open: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])

const auth = useAuthStore()
const route = useRoute()

const MENU = [
  { to: '/dashboard', label: 'Tableau de bord', icon: LayoutDashboard },
  { to: '/transformateurs', label: 'Transformateurs', icon: Zap },
  { to: '/carte', label: 'Carte géographique', icon: Map },
  { to: '/charge', label: 'Suivi de charge', icon: Gauge },
  { to: '/inspections', label: 'Inspections', icon: ClipboardCheck },
  { to: '/interventions', label: 'Interventions', icon: Wrench },
  { to: '/pannes', label: 'Pannes', icon: ShieldAlert },
  { to: '/utilisateurs', label: 'Utilisateurs', icon: Users, roles: ['ADMIN'] },
]

const items = computed(() =>
  MENU.filter((item) => !item.roles || item.roles.includes(auth.role)),
)

const initiales = computed(() => {
  const u = auth.user
  if (!u) return '?'
  return `${u.prenom?.[0] ?? ''}${u.nom?.[0] ?? ''}`.toUpperCase() || '?'
})

// Referme le menu mobile après chaque navigation.
watch(
  () => route.path,
  () => emit('close'),
)

function logout() {
  auth.logout()
}
</script>

<template>
  <!-- Overlay mobile -->
  <div
    v-if="open"
    class="fixed inset-0 z-30 bg-slate-900/60 backdrop-blur-sm lg:hidden"
    @click="emit('close')"
  ></div>

  <!-- Sidebar principale -->
  <aside
    class="fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-[#0F1F3D] text-slate-100 shadow-2xl transition-transform duration-200 lg:static lg:translate-x-0"
    :class="open ? 'translate-x-0' : '-translate-x-full'"
  >
    <!-- En-tête / Logo -->
    <div class="flex h-16 items-center gap-3 border-b border-white/10 px-5">
      <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white text-[#0F1F3D]">
        <Zap class="h-5 w-5" />
      </div>
      <div class="leading-tight">
        <p class="text-sm font-bold tracking-wide text-white">JIRAMA</p>
        <p class="text-[11px] text-slate-300">Transformateurs</p>
      </div>
      <!-- Bouton fermer mobile -->
      <button
        @click="emit('close')"
        class="ml-auto rounded p-1 text-slate-400 hover:bg-white/10 hover:text-white lg:hidden"
        aria-label="Fermer le menu"
      >
        <X class="h-5 w-5" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4" aria-label="Navigation principale">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        custom
        v-slot="{ href, navigate, isActive }"
      >
        <a
          :href="href"
          class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
          :class="
            isActive
              ? 'bg-blue-600 text-white shadow-md shadow-blue-900/40'
              : 'text-slate-300 hover:bg-white/10 hover:text-white'
          "
          :aria-current="isActive ? 'page' : undefined"
          @click="navigate"
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          {{ item.label }}
        </a>
      </RouterLink>
    </nav>

    <!-- Pied : Profil + Déconnexion -->
    <div class="border-t border-white/10 p-4 space-y-3">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
          {{ initiales }}
        </div>
        <div class="min-w-0 leading-tight">
          <p class="truncate text-sm font-semibold text-white">{{ auth.fullName }}</p>
          <p class="text-xs text-slate-400">{{ ROLE_LABELS[auth.role] }}</p>
        </div>
      </div>
      <button
        @click="logout"
        class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition-colors hover:bg-red-500/10 hover:text-red-400"
      >
        <LogOut class="h-4 w-4" />
        Déconnexion
      </button>
    </div>
  </aside>
</template>