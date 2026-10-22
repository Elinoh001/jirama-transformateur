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

defineProps({
  open: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])

const auth = useAuthStore()
const route = useRoute()

const MENU = [
  { to: '/dashboard', label: 'Tableau de bord', icon: LayoutDashboard },
  { to: '/transformateurs', label: 'Transformateurs', icon: Zap },
  { to: '/carte', label: 'Carte', icon: Map },
  { to: '/charge', label: 'Suivi de charge', icon: Gauge },
  { to: '/inspections', label: 'Inspections', icon: ClipboardCheck },
  { to: '/interventions', label: 'Interventions', icon: Wrench },
  { to: '/pannes', label: 'Pannes', icon: ShieldAlert },
  { to: '/utilisateurs', label: 'Utilisateurs', icon: Users, roles: ['ADMIN'] },
]

const items = computed(() =>
  MENU.filter((item) => !item.roles || item.roles.includes(auth.role)),
)

// Referme le menu mobile après chaque navigation.
watch(
  () => route.path,
  () => emit('close'),
)
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 z-30 bg-slate-900/50 lg:hidden"
    @click="emit('close')"
  ></div>

  <aside
    class="fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-slate-900 text-slate-100 transition-transform duration-200 lg:static lg:translate-x-0"
    :class="open ? 'translate-x-0' : '-translate-x-full'"
  >
    <div class="flex h-16 items-center gap-3 border-b border-slate-800 px-5">
      <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-yellow-400 text-slate-900">
        <Zap class="h-5 w-5" />
      </div>
      <div class="leading-tight">
        <p class="text-sm font-bold tracking-wide">JIRAMA</p>
        <p class="text-xs text-slate-400">Suivi des transformateurs</p>
      </div>
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        custom
        v-slot="{ href, navigate, isActive }"
      >
        <a
          :href="href"
          class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
          :class="
            isActive
              ? 'bg-blue-600 text-white'
              : 'text-slate-300 hover:bg-slate-800 hover:text-white'
          "
          @click="navigate"
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          {{ item.label }}
        </a>
      </RouterLink>
    </nav>

    <div class="border-t border-slate-800 px-5 py-3 text-xs text-slate-500">
      JIRAMA Antsirabe · Projet L3
    </div>
  </aside>
</template>