import api from './api'

export default {
  async list(params = {}) {
    const { data } = await api.get('/inspections', { params })
    return data
  },

  async create(payload) {
    const { data } = await api.post('/inspections', payload)
    return data
  },

  async update(id, payload) {
    const { data } = await api.put(`/inspections/${id}`, payload)
    return data
  },
}