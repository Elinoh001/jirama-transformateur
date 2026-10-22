import api from './api'

export default {
  async list(params = {}) {
    const { data } = await api.get('/pannes', { params })
    return data
  },

  async create(payload) {
    const { data } = await api.post('/pannes', payload)
    return data
  },

  async update(id, payload) {
    const { data } = await api.put(`/pannes/${id}`, payload)
    return data
  },
}