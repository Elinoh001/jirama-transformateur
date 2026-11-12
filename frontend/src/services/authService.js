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

  async changePassword(ancien, nouveau) {
    const { data } = await api.post('/auth/change-password', {
      ancien_mot_de_passe: ancien,
      nouveau_mot_de_passe: nouveau,
    })
    return data // { message }
  },
}