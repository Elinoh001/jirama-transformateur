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

const NOMS_CHAMPS = {
  reference: 'Référence',
  nom: 'Nom',
  secteur: 'Quartier',
  puissance: 'Puissance',
  tension_mt: 'Tension MT',
  tension_bt: 'Tension BT',
  latitude: 'Latitude',
  longitude: 'Longitude',
  periodicite_inspection_mois: 'Périodicité',
  date_inspection: "Date d'inspection",
  date_intervention: "Date d'intervention",
  date_releve: 'Date du relevé',
  valeur: 'Valeur mesurée',
  description: 'Description',
  actions_correctives: 'Actions correctives',
  email: 'E-mail',
  mot_de_passe: 'Mot de passe',
  nouveau_mot_de_passe: 'Nouveau mot de passe',
  ancien_mot_de_passe: 'Mot de passe actuel',
  cout: 'Coût',
}

/** Traduit les messages techniques de validation (Pydantic) en phrases lisibles. */
function traduireMessage(msg) {
  let m = String(msg || '').replace(/^Value error, /, '')
  const rules = [
    [/^Field required$/i, 'champ obligatoire'],
    [/^String should have at least (\d+) characters?/i, (r) => `${r[1]} caractère(s) minimum`],
    [/^String should have at most (\d+) characters?/i, (r) => `${r[1]} caractère(s) maximum`],
    [/^Input should be greater than or equal to (.+)/i, (r) => `doit être supérieur ou égal à ${r[1]}`],
    [/^Input should be greater than (.+)/i, (r) => `doit être supérieur à ${r[1]}`],
    [/^Input should be less than or equal to (.+)/i, (r) => `doit être inférieur ou égal à ${r[1]}`],
    [/^Input should be less than (.+)/i, (r) => `doit être inférieur à ${r[1]}`],
    [/^Input should be a valid (number|integer)/i, () => 'nombre invalide'],
    [/^Input should be a valid (date|datetime)/i, () => 'date invalide'],
    [/^value is not a valid email address.*/i, () => 'adresse e-mail invalide'],
    [/^Input should be /i, () => 'valeur non autorisée'],
  ]
  for (const [re, out] of rules) {
    const r = m.match(re)
    if (r) return typeof out === 'function' ? out(r) : out
  }
  return m
}

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
        const cle = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : ''
        const champ = typeof cle === 'string' ? NOMS_CHAMPS[cle] || '' : ''
        const texte = traduireMessage(d.msg)
        return champ ? `${champ} : ${texte}` : texte
      })
      .join(' ; ')
  }
  return fallback
}

export default api