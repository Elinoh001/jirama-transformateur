import api from './api'

export default {
  async login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    return data // { access_token, token_type, user }
  },

  async me() {
    const { data } = await api.get('/auth/me')
    return data
  },
}