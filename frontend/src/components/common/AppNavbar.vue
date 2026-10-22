<script setup>
import { LogOut, Menu } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/authStore'
import { useDashboardStore } from '@/stores/dashboardStore'
import { ROLE_LABELS } from '@/utils/format'

const emit = defineEmits(['toggle-sidebar'])

const auth = useAuthStore()
const dashboard = useDashboardStore()
const route = useRoute()
const router = useRouter()

function deconnecter() {
  auth.logout()
  dashboard.reset()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6">
    <div class="flex items-center gap-3">
      <button
        type="button"
        class="cursor-pointer rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
        aria-label="Ouvrir le menu"
        @click="emit('toggle-sidebar')"
      >
        <Menu class="h-5 w-5" />
      </button>
      <h1 class="text-lg font-semibold text-slate-800">{{ route.meta.title }}</h1>
    </div>

    <div class="flex items-center gap-4">
      <div class="hidden text-right leading-tight sm:block">
        <p class="text-sm font-medium text-slate-800">{{ auth.fullName }}</p>
        <p class="text-xs text-slate-500">{{ ROLE_LABELS[auth.role] }}</p>
      </div>
      <button
        type="button"
        class="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        @click="deconnecter"
      >
        <LogOut class="h-4 w-4" />
        <span class="hidden sm:inline">Déconnexion</span>
      </button>
    </div>
  </header>
</template>