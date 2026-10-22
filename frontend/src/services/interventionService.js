import api from './api'

export default {
  async list(params = {}) {
    const { data } = await api.get('/interventions', { params })
    return data
  },

  async create(payload) {
    const { data } = await api.post('/interventions', payload)
    return data
  },

  async update(id, payload) {
    const { data } = await api.put(`/interventions/${id}`, payload)
    return data
  },
}