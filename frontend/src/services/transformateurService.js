import api from './api'

export default {
  async list(params = {}) {
    const { data } = await api.get('/transformateurs', { params })
    return data
  },

  async secteurs() {
    const { data } = await api.get('/transformateurs/secteurs')
    return data
  },

  async get(id) {
    const { data } = await api.get(`/transformateurs/${id}`)
    return data
  },

  async historique(id, ordre = 'desc') {
    const { data } = await api.get(`/transformateurs/${id}/historique`, { params: { ordre } })
    return data
  },

  async create(payload) {
    const { data } = await api.post('/transformateurs', payload)
    return data
  },

  async update(id, payload) {
    const { data } = await api.put(`/transformateurs/${id}`, payload)
    return data
  },

  async remove(id) {
    await api.delete(`/transformateurs/${id}`)
  },
}