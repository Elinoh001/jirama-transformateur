import api from './api'

export default {
  async getStatistics() {
    const { data } = await api.get('/dashboard/statistics')
    return data
  },

  async getPriorities(params = {}) {
    const { data } = await api.get('/dashboard/priorities', { params })
    return data
  },

  /** { en_retard, items: [...] } */
  async getUpcomingInspections(params = {}) {
    const { data } = await api.get('/dashboard/inspections-a-venir', { params })
    return data
  },
}