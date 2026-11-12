<script setup>
import { computed, reactive, watch } from 'vue'

import { STATUT_LABELS, TYPE_INTERVENTION_LABELS, joursEcoules, todayISO } from '@/utils/format'
import { btnPrimary, btnSecondary, inputClass, labelClass } from '@/utils/ui'

const props = defineProps({
  intervention: { type: Object, default: null }, // null = création
  transformateurs: { type: Array, default: () => [] }, // [{ id, reference, nom }]
  lockedId: { type: Number, default: null }, // transformateur imposé (page de détail)
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])

const today = todayISO()
const iv = props.intervention
const form = reactive({
  transformateur_id: iv?.transformateur_id ?? props.lockedId ?? '',
  date_intervention: iv?.date_intervention ?? today,
  type: iv?.type ?? 'PREVENTIVE',
  statut: iv?.statut ?? 'PLANIFIEE',
  cout: iv?.cout ?? '',
  description: iv?.description ?? '',
  technicien: iv?.technicien ?? '',
})

// Règles du backend :
// - planifiée -> en cours, terminée ou annulée ; en cours -> terminée ou annulée ;
// - terminée : figée, seuls le coût et le compte-rendu (description) restent modifiables ;
// - annulée : archivée, lecture seule ;
// - un compte-rendu est obligatoire pour terminer ; la date d'une intervention commencée ou terminée n'est pas future.
const figee = computed(() => props.intervention?.statut === 'TERMINEE')
const archivee = computed(() => props.intervention?.statut === 'ANNULEE')
const lectureSeule = computed(() => figee.value || archivee.value)

const verrouille = computed(() => !!props.intervention || props.lockedId !== null)

const statutsPossibles = computed(() => {
  const courant = props.intervention?.statut
  if (!courant) return ['PLANIFIEE', 'EN_COURS', 'TERMINEE']
  if (courant === 'PLANIFIEE') return ['PLANIFIEE', 'EN_COURS', 'TERMINEE', 'ANNULEE']
  if (courant === 'EN_COURS') return ['EN_COURS', 'TERMINEE', 'ANNULEE']
  return [courant]
})

const planifiee = computed(() => form.statut === 'PLANIFIEE')
const termine = computed(() => form.statut === 'TERMINEE')
const annulation = computed(() => !!props.intervention && form.statut === 'ANNULEE' && !lectureSeule.value)

// Intervention planifiée dont la date est passée : en retard.
const retardJours = computed(() => {
  if (props.intervention?.statut !== 'PLANIFIEE' || !planifiee.value) return 0
  if (form.date_intervention !== props.intervention.date_intervention) return 0
  return Math.max(0, joursEcoules(props.intervention.date_intervention))
})

// En cours ou terminée : la date ne peut pas être dans le futur.
watch(
  () => form.statut,
  (statut) => {
    if ((statut === 'EN_COURS' || statut === 'TERMINEE') && form.date_intervention > today) {
      form.date_intervention = today
    }
    if (statut === 'PLANIFIEE' && form.date_intervention < today && !props.intervention) {
      form.date_intervention = today
    }
  },
)

const dateMin = computed(() => {
  if (!planifiee.value) return undefined
  if (props.intervention && form.date_intervention === props.intervention.date_intervention) return undefined
  return today
})
const dateMax = computed(() => (form.statut === 'EN_COURS' || termine.value ? today : undefined))

function submit() {
  if (archivee.value) return
  const description = form.description.trim() || null
  const cout = form.cout === '' || form.cout === null ? null : Number(form.cout)

  // Intervention terminée : seuls le coût et le compte-rendu sont envoyés.
  if (figee.value) {
    emit('submit', { description, cout })
    return
  }
  // Annulation : le statut suffit.
  if (annulation.value) {
    emit('submit', { statut: 'ANNULEE' })
    return
  }

  const payload = {
    date_intervention: form.date_intervention,
    type: form.type,
    statut: form.statut,
    cout,
    description,
  }
  // Technicien vide : le backend utilise le nom de l'utilisateur connecté.
  if (form.technicien.trim()) payload.technicien = form.technicien.trim()
  if (!props.intervention) payload.transformateur_id = Number(form.transformateur_id)
  emit('submit', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <p v-if="figee" class="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700">
      Intervention terminée : elle est figée pour conserver l'historique d'entretien. Seuls le coût et le
      compte-rendu peuvent être complétés.
    </p>
    <p v-else-if="archivee" class="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700">
      Intervention annulée : elle est archivée et ne peut plus être modifiée.
    </p>
    <p v-else-if="retardJours > 0" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
      Cette intervention est en retard de {{ retardJours }} jour(s). Reportez-la, démarrez-la ou annulez-la.
    </p>

    <div>
      <label for="v-trans" :class="labelClass">Transformateur</label>
      <select id="v-trans" v-model="form.transformateur_id" required :disabled="verrouille" :class="inputClass">
        <option value="" disabled>Choisir...</option>
        <option v-for="t in transformateurs" :key="t.id" :value="t.id">{{ t.reference }} — {{ t.nom }}</option>
      </select>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div>
        <label for="v-date" :class="labelClass">Date</label>
        <input
          id="v-date"
          v-model="form.date_intervention"
          type="date"
          :min="dateMin"
          :max="dateMax"
          required
          :disabled="lectureSeule || annulation"
          :class="inputClass"
        />
      </div>
      <div>
        <label for="v-type" :class="labelClass">Type</label>
        <select id="v-type" v-model="form.type" :disabled="lectureSeule || annulation" :class="inputClass">
          <option v-for="(label, value) in TYPE_INTERVENTION_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div>
        <label for="v-statut" :class="labelClass">Statut</label>
        <select
          id="v-statut"
          v-model="form.statut"
          :disabled="statutsPossibles.length === 1 || lectureSeule"
          :class="inputClass"
        >
          <option v-for="s in statutsPossibles" :key="s" :value="s">{{ STATUT_LABELS[s] }}</option>
        </select>
      </div>
    </div>

    <p v-if="form.statut === 'EN_COURS'" class="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">
      Pendant une intervention en cours, le transformateur passe « En maintenance ».
    </p>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="v-cout" :class="labelClass">Coût (Ar)</label>
        <input
          id="v-cout"
          v-model="form.cout"
          type="number"
          min="0"
          step="any"
          :disabled="archivee || annulation"
          :class="inputClass"
        />
      </div>
      <div>
        <label for="v-tech" :class="labelClass">Technicien</label>
        <input
          id="v-tech"
          v-model="form.technicien"
          maxlength="150"
          :disabled="lectureSeule || annulation"
          placeholder="Laisser vide pour utiliser votre nom"
          :class="inputClass"
        />
      </div>
    </div>

    <div>
      <label for="v-desc" :class="labelClass">
        {{ termine || figee ? 'Compte-rendu (obligatoire)' : 'Description' }}
      </label>
      <textarea
        id="v-desc"
        v-model="form.description"
        rows="3"
        maxlength="2000"
        :required="termine || figee"
        :disabled="archivee || annulation"
        :class="inputClass"
      ></textarea>
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="btnSecondary" :disabled="saving" @click="emit('cancel')">
        {{ archivee ? 'Fermer' : 'Annuler' }}
      </button>
      <button v-if="!archivee" type="submit" :class="btnPrimary" :disabled="saving">
        {{ saving ? 'Enregistrement...' : annulation ? "Confirmer l'annulation" : 'Enregistrer' }}
      </button>
    </div>
  </form>
</template>
