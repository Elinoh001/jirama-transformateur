<script setup>
import { computed, reactive, watch } from 'vue'

import {
  ETAT_HUILE_LABELS,
  ETAT_LABELS,
  STATUT_INSPECTION_LABELS,
  TYPE_INSPECTION_LABELS,
  joursEcoules,
  todayISO,
} from '@/utils/format'
import { btnPrimary, btnSecondary, inputClass, labelClass } from '@/utils/ui'

const props = defineProps({
  inspection: { type: Object, default: null }, // null = création
  transformateurs: { type: Array, default: () => [] }, // [{ id, reference, nom }]
  lockedId: { type: Number, default: null }, // transformateur imposé (page de détail)
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])

const today = todayISO()
const i = props.inspection
const form = reactive({
  transformateur_id: i?.transformateur_id ?? props.lockedId ?? '',
  date_inspection: i?.date_inspection ?? today,
  type: i?.type ?? 'ROUTINE',
  statut: i?.statut ?? 'REALISEE',
  etat: i?.etat ?? 'BON',
  etat_huile: i?.etat_huile ?? '',
  observation: i?.observation ?? '',
  technicien: i?.technicien ?? '',
})

// Règles du backend :
// - planifiée : modifiable (report), réalisable, annulable ;
// - réalisée : figée (historique conservé), seule l'observation peut être complétée ;
// - annulée : archivée, lecture seule.
const figee = computed(() => props.inspection?.statut === 'REALISEE')
const archivee = computed(() => props.inspection?.statut === 'ANNULEE')
const lectureSeule = computed(() => figee.value || archivee.value)

// Le transformateur d'une inspection existante ne peut pas être changé.
const verrouille = computed(() => !!props.inspection || props.lockedId !== null)

// Statuts proposés : une inspection réalisée ne redevient jamais planifiée.
const statutsPossibles = computed(() => {
  if (!props.inspection) return ['REALISEE', 'PLANIFIEE']
  if (props.inspection.statut === 'PLANIFIEE') return ['PLANIFIEE', 'REALISEE', 'ANNULEE']
  return [props.inspection.statut]
})

const realisee = computed(() => form.statut === 'REALISEE')
const planifiee = computed(() => form.statut === 'PLANIFIEE')
const annulation = computed(() => !!props.inspection && form.statut === 'ANNULEE' && !lectureSeule.value)

// Une inspection planifiée dont la date est passée est en retard : il faut la reporter ou la réaliser.
const retardJours = computed(() => {
  if (props.inspection?.statut !== 'PLANIFIEE' || !planifiee.value) return 0
  if (form.date_inspection !== props.inspection.date_inspection) return 0
  return Math.max(0, joursEcoules(props.inspection.date_inspection))
})

// Réalisée : date aujourd'hui ou passée. Planifiée : date aujourd'hui ou future.
watch(
  () => form.statut,
  (statut) => {
    if (statut === 'REALISEE' && form.date_inspection > today) form.date_inspection = today
    if (statut === 'PLANIFIEE' && form.date_inspection < today && !props.inspection) form.date_inspection = today
  },
)

// Date minimale d'une planification : aujourd'hui, sauf si la date existante (en retard) n'est pas touchée.
const dateMin = computed(() => {
  if (!planifiee.value) return undefined
  if (props.inspection && form.date_inspection === props.inspection.date_inspection) return undefined
  return today
})

function submit() {
  if (lectureSeule.value && !figee.value) return
  const observation = form.observation.trim() || null

  // Inspection réalisée : seule l'observation est envoyée.
  if (figee.value) {
    emit('submit', { observation })
    return
  }
  // Annulation : le statut et le motif (observation) suffisent.
  if (annulation.value) {
    emit('submit', { statut: 'ANNULEE', observation })
    return
  }

  const payload = {
    date_inspection: form.date_inspection,
    type: form.type,
    statut: form.statut,
    observation,
  }
  // Technicien vide : le backend utilise le nom de l'utilisateur connecté.
  if (form.technicien.trim()) payload.technicien = form.technicien.trim()
  if (realisee.value) {
    payload.etat = form.etat
    payload.etat_huile = form.etat_huile || null
  }
  if (!props.inspection) payload.transformateur_id = Number(form.transformateur_id)
  emit('submit', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <p v-if="figee" class="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700">
      Inspection réalisée : elle est figée pour conserver l'historique. Seule l'observation peut être complétée.
    </p>
    <p v-else-if="archivee" class="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700">
      Inspection annulée : elle est archivée et ne peut plus être modifiée.
    </p>
    <p v-else-if="retardJours > 0" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
      Cette inspection est en retard de {{ retardJours }} jour(s). Reportez-la à une nouvelle date, marquez-la
      comme réalisée ou annulez-la.
    </p>

    <div>
      <label for="i-trans" :class="labelClass">Transformateur</label>
      <select id="i-trans" v-model="form.transformateur_id" required :disabled="verrouille" :class="inputClass">
        <option value="" disabled>Choisir...</option>
        <option v-for="t in transformateurs" :key="t.id" :value="t.id">{{ t.reference }} — {{ t.nom }}</option>
      </select>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div>
        <label for="i-statut" :class="labelClass">Statut</label>
        <select
          id="i-statut"
          v-model="form.statut"
          :disabled="statutsPossibles.length === 1 || lectureSeule"
          :class="inputClass"
        >
          <option v-for="s in statutsPossibles" :key="s" :value="s">{{ STATUT_INSPECTION_LABELS[s] }}</option>
        </select>
      </div>
      <div>
        <label for="i-date" :class="labelClass">{{ planifiee ? 'Date programmée' : 'Date' }}</label>
        <input
          id="i-date"
          v-model="form.date_inspection"
          type="date"
          :max="realisee && !lectureSeule ? today : undefined"
          :min="dateMin"
          required
          :disabled="lectureSeule || annulation"
          :class="inputClass"
        />
      </div>
      <div>
        <label for="i-type" :class="labelClass">Nature</label>
        <select id="i-type" v-model="form.type" :disabled="lectureSeule || annulation" :class="inputClass">
          <option v-for="(label, value) in TYPE_INSPECTION_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
    </div>

    <div v-if="realisee" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="i-etat" :class="labelClass">État constaté</label>
        <select id="i-etat" v-model="form.etat" required :disabled="lectureSeule" :class="inputClass">
          <option v-for="(label, value) in ETAT_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div>
        <label for="i-huile" :class="labelClass">État de l'huile</label>
        <select id="i-huile" v-model="form.etat_huile" :disabled="lectureSeule" :class="inputClass">
          <option value="">Non renseigné</option>
          <option v-for="(label, value) in ETAT_HUILE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
    </div>
    <p v-else-if="planifiee" class="rounded-lg bg-blue-50 px-3 py-2 text-xs text-blue-800">
      Inspection programmée : l'état constaté sera renseigné quand elle sera réalisée. Cette date devient la
      prochaine inspection prévue du transformateur.
    </p>
    <p v-else-if="annulation" class="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">
      Après annulation, la prochaine échéance du transformateur est recalculée automatiquement. Indiquez le motif
      dans l'observation.
    </p>

    <div>
      <label for="i-obs" :class="labelClass">{{ annulation ? "Motif de l'annulation" : 'Observation' }}</label>
      <textarea
        id="i-obs"
        v-model="form.observation"
        rows="3"
        maxlength="2000"
        :disabled="archivee"
        :class="inputClass"
      ></textarea>
    </div>

    <div>
      <label for="i-tech" :class="labelClass">Technicien</label>
      <input
        id="i-tech"
        v-model="form.technicien"
        maxlength="150"
        :disabled="lectureSeule || annulation"
        placeholder="Laisser vide pour utiliser votre nom"
        :class="inputClass"
      />
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="btnSecondary" :disabled="saving" @click="emit('cancel')">
        {{ archivee ? 'Fermer' : 'Annuler' }}
      </button>
      <button v-if="!archivee" type="submit" :class="btnPrimary" :disabled="saving">
        {{ saving ? 'Enregistrement...' : figee ? "Enregistrer l'observation" : annulation ? "Confirmer l'annulation" : 'Enregistrer' }}
      </button>
    </div>
  </form>
</template>
