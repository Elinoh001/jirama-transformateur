import api from './api'

export default {
  async list(params = {}) {
    const { data } = await api.get('/releves-charge', { params })
    return data
  },

  async create(payload) {
    const { data } = await api.post('/releves-charge', payload)
    return data
  },
}