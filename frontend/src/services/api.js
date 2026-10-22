import axios from 'axios'

export const TOKEN_KEY = 'jirama_token'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Ajoute automatiquement : Authorization: Bearer <token>
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Token expiré ou invalide : on le supprime et on renvoie vers /login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const estConnexion = error.config?.url?.includes('/auth/login')
    if (status === 401 && !estConnexion) {
      localStorage.removeItem(TOKEN_KEY)
      if (window.location.pathname !== '/login') {
        window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  },
)

/** Extrait un message lisible d'une erreur Axios / FastAPI. */
export function getErrorMessage(error, fallback = 'Une erreur est survenue') {
  if (!error.response) {
    return 'Impossible de joindre le serveur. Vérifiez que le backend est démarré.'
  }
  const detail = error.response.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((d) => {
        const champ = Array.isArray(d.loc) ? d.loc.slice(1).join('.') : ''
        return champ ? `${champ} : ${d.msg}` : d.msg
      })
      .join(' ; ')
  }
  return fallback
}

export default api