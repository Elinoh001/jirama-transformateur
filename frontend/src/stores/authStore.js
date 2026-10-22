import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import authService from '@/services/authService'
import { TOKEN_KEY } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // Le token est conservé dans localStorage (clé unique : jirama_token).
  const token = ref(localStorage.getItem(TOKEN_KEY))
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const role = computed(() => user.value?.role ?? null)
  const fullName = computed(() => (user.value ? `${user.value.prenom} ${user.value.nom}` : ''))

  // Permissions d'affichage. Le backend reste la vraie sécurité.
  const isAdmin = computed(() => role.value === 'ADMIN')
  const canManageUsers = computed(() => role.value === 'ADMIN')
  const canManageTransformateurs = computed(() => role.value === 'ADMIN')
  const canWriteTerrain = computed(() => ['ADMIN', 'AGENT'].includes(role.value)) // inspections, interventions
  const canViewStatistics = computed(() => ['ADMIN', 'SUPERVISEUR'].includes(role.value))

  async function login(email, password) {
    const data = await authService.login(email, password)
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem(TOKEN_KEY, data.access_token)
  }

  async function fetchCurrentUser() {
    user.value = await authService.me()
    return user.value
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return {
    token,
    user,
    isAuthenticated,
    role,
    fullName,
    isAdmin,
    canManageUsers,
    canManageTransformateurs,
    canWriteTerrain,
    canViewStatistics,
    login,
    fetchCurrentUser,
    logout,
  }
})