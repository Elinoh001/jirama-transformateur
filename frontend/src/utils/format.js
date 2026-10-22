export const ROLE_LABELS = {
  ADMIN: 'Administrateur',
  SUPERVISEUR: 'Superviseur',
  AGENT: 'Agent',
}

export const ETAT_LABELS = {
  BON: 'Bon',
  A_SURVEILLER: 'À surveiller',
  CRITIQUE: 'Critique',
}

export const PRIORITE_LABELS = {
  NORMAL: 'Normal',
  A_SURVEILLER: 'À surveiller',
  PRIORITAIRE: 'Prioritaire',
}

export const STATUT_LABELS = {
  PLANIFIEE: 'Planifiée',
  EN_COURS: 'En cours',
  TERMINEE: 'Terminée',
  ANNULEE: 'Annulée',
}

export const TYPE_INSPECTION_LABELS = {
  ROUTINE: 'Routine',
  VISUELLE: 'Visuelle',
  THERMIQUE: 'Thermique',
  POST_INCIDENT: 'Post-incident',
}

export const TYPE_INTERVENTION_LABELS = {
  PREVENTIVE: 'Préventive',
  CORRECTIVE: 'Corrective',
  REMPLACEMENT: 'Remplacement',
}

export const STATUT_OPERATIONNEL_LABELS = {
  EN_SERVICE: 'En service',
  EN_SURCHARGE: 'En surcharge',
  EN_MAINTENANCE: 'En maintenance',
  EN_PANNE: 'En panne',
}

export const NIVEAU_HUILE_LABELS = {
  NORMAL: 'Normal',
  BAS: 'Bas',
  CRITIQUE: 'Critique',
}

export const STATUT_INSPECTION_LABELS = {
  PLANIFIEE: 'Planifiée',
  REALISEE: 'Réalisée',
  ANNULEE: 'Annulée',
}

export const ETAT_HUILE_LABELS = {
  BONNE: 'Bonne',
  DEGRADEE: 'Dégradée',
  CONTAMINEE: 'Contaminée',
}

export const TYPE_PANNE_LABELS = {
  FUITE_HUILE: "Fuite d'huile",
  SURCHAUFFE: 'Surchauffe',
  COUPURE: 'Coupure',
  ANOMALIE_MECANIQUE: 'Anomalie mécanique',
}

export const GRAVITE_LABELS = {
  MINEURE: 'Mineure',
  MAJEURE: 'Majeure',
  CRITIQUE: 'Critique',
}

export const STATUT_PANNE_LABELS = {
  SIGNALEE: 'Signalée',
  EN_COURS: 'En cours',
  RESOLUE: 'Résolue',
}

/** Libellé lisible d'une valeur d'énumération (retourne la valeur brute si inconnue). */
export function labelOf(map, key) {
  return map[key] ?? key ?? '—'
}

/** "2026-09-18" -> "18/09/2026" (sans passer par Date, pour éviter les décalages de fuseau). */
export function formatDate(value) {
  if (!value) return '—'
  const [annee, mois, jour] = String(value).slice(0, 10).split('-')
  return `${jour}/${mois}/${annee}`
}

/** Date et heure locales, pour les horodatages (signalement de panne). */
export function formatDateTime(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
}

export function formatMontant(value) {
  return `${Number(value || 0).toLocaleString('fr-FR')} Ar`
}

export function formatPourcent(value) {
  if (value === null || value === undefined) return '—'
  return `${Number(value).toLocaleString('fr-FR', { maximumFractionDigits: 1 })} %`
}

/** Date du jour au format AAAA-MM-JJ, en heure locale (pas UTC). */
export function todayISO() {
  const d = new Date()
  const mois = String(d.getMonth() + 1).padStart(2, '0')
  const jour = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mois}-${jour}`
}