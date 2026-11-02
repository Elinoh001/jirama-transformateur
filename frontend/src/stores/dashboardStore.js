import { ref } from 'vue'
import { defineStore } from 'pinia'

import dashboardService from '@/services/dashboardService'
import { getErrorMessage } from '@/services/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const statistics = ref(null)
  const priorities = ref([])
  const upcoming = ref(null) // { en_retard, items } ; null si indisponible
  const loading = ref(false)
  const error = ref('')

  /** withStatistics = false pour l'AGENT (le backend lui refuse /statistics). */
  async function fetchAll(withStatistics = true) {
    loading.value = true
    error.value = ''
    try {
      const [stats, prios, echeances] = await Promise.all([
        withStatistics ? dashboardService.getStatistics() : Promise.resolve(null),
        dashboardService.getPriorities({ limit: 10 }),
        // Les échéances ne doivent jamais bloquer le reste du tableau de bord.
        dashboardService.getUpcomingInspections({ limit: 5 }).catch(() => null),
      ])
      statistics.value = stats
      priorities.value = prios
      upcoming.value = echeances
    } catch (e) {
      error.value = getErrorMessage(e, 'Impossible de charger le tableau de bord')
    } finally {
      loading.value = false
    }
  }

  function reset() {
    statistics.value = null
    priorities.value = []
    upcoming.value = null
    error.value = ''
  }

  return { statistics, priorities, upcoming, loading, error, fetchAll, reset }
})