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
} from 'lucide-vue-next'

import { useAuthStore } from '@/stores/authStore'
import { ROLE_LABELS } from '@/utils/format'

defineProps({
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
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 z-30 bg-navy-950/60 lg:hidden"
    @click="emit('close')"
  ></div>

  <aside
    class="fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-gradient-to-b from-navy-900 to-navy-950 text-slate-100 shadow-xl transition-transform duration-200 lg:static lg:translate-x-0"
    :class="open ? 'translate-x-0' : '-translate-x-full'"
  >
    <div class="flex h-20 items-center gap-3 border-b border-white/10 px-5">
      <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border-2 border-white/80 text-white">
        <Zap class="h-6 w-6" />
      </div>
      <div class="leading-tight">
        <p class="text-lg font-bold tracking-wide text-white">JIRAMA</p>
        <p class="text-xs text-blue-200">Transformateurs</p>
      </div>
    </div>

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
              : 'text-blue-100/80 hover:bg-white/10 hover:text-white'
          "
          :aria-current="isActive ? 'page' : undefined"
          @click="navigate"
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          {{ item.label }}
        </a>
      </RouterLink>
    </nav>

    <div class="border-t border-white/10 p-4">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
          {{ initiales }}
        </div>
        <div class="min-w-0 leading-tight">
          <p class="truncate text-sm font-semibold text-white">{{ auth.fullName }}</p>
          <p class="text-xs text-blue-200">{{ ROLE_LABELS[auth.role] }}</p>
        </div>
      </div>
    </div>
  </aside>
</template>