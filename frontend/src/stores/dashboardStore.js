import { ref } from 'vue'
import { defineStore } from 'pinia'

import dashboardService from '@/services/dashboardService'
import { getErrorMessage } from '@/services/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const statistics = ref(null)
  const priorities = ref([])
  const loading = ref(false)
  const error = ref('')

  /** withStatistics = false pour l'AGENT (le backend lui refuse /statistics). */
  async function fetchAll(withStatistics = true) {
    loading.value = true
    error.value = ''
    try {
      const [stats, prios] = await Promise.all([
        withStatistics ? dashboardService.getStatistics() : Promise.resolve(null),
        dashboardService.getPriorities({ limit: 10 }),
      ])
      statistics.value = stats
      priorities.value = prios
    } catch (e) {
      error.value = getErrorMessage(e, 'Impossible de charger le tableau de bord')
    } finally {
      loading.value = false
    }
  }

  function reset() {
    statistics.value = null
    priorities.value = []
    error.value = ''
  }

  return { statistics, priorities, loading, error, fetchAll, reset }
})