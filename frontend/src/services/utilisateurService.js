import api from './api'

export default {
  async list() {
    const { data } = await api.get('/utilisateurs')
    return data
  },

  async create(payload) {
    const { data } = await api.post('/utilisateurs', payload)
    return data
  },

  async update(id, payload) {
    const { data } = await api.put(`/utilisateurs/${id}`, payload)
    return data
  },

  async remove(id) {
    await api.delete(`/utilisateurs/${id}`)
  },
}