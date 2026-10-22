<script setup>
import { reactive } from 'vue'

import { ETAT_LABELS, NIVEAU_HUILE_LABELS } from '@/utils/format'
import { btnPrimary, btnSecondary, inputClass, labelClass } from '@/utils/ui'

const props = defineProps({
  transformateur: { type: Object, default: null }, // null = création
  secteurs: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])

const t = props.transformateur
const form = reactive({
  reference: t?.reference ?? '',
  nom: t?.nom ?? '',
  secteur: t?.secteur ?? '',
  puissance: t?.puissance ?? '',
  tension_mt: t?.tension_mt ?? 20,
  tension_bt: t?.tension_bt ?? 400,
  type_huile: t?.type_huile ?? '',
  niveau_huile: t?.niveau_huile ?? 'NORMAL',
  date_installation: t?.date_installation ?? '',
  etat: t?.etat ?? 'BON',
  periodicite_inspection_mois: t?.periodicite_inspection_mois ?? 12,
  latitude: t?.latitude ?? '',
  longitude: t?.longitude ?? '',
  actif: t?.actif ?? true,
})

function submit() {
  emit('submit', {
    reference: form.reference.trim(),
    nom: form.nom.trim(),
    secteur: form.secteur,
    puissance: Number(form.puissance),
    tension_mt: Number(form.tension_mt),
    tension_bt: Number(form.tension_bt),
    type_huile: form.type_huile.trim() || null,
    niveau_huile: form.niveau_huile,
    date_installation: form.date_installation || null,
    etat: form.etat,
    periodicite_inspection_mois: Number(form.periodicite_inspection_mois),
    latitude: Number(form.latitude),
    longitude: Number(form.longitude),
    actif: form.actif,
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="t-ref" :class="labelClass">Référence</label>
        <input id="t-ref" v-model="form.reference" required maxlength="50" placeholder="TR-009" :class="inputClass" />
      </div>
      <div>
        <label for="t-nom" :class="labelClass">Nom du poste</label>
        <input id="t-nom" v-model="form.nom" required maxlength="150" placeholder="Poste ..." :class="inputClass" />
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="t-secteur" :class="labelClass">Quartier / secteur</label>
        <select id="t-secteur" v-model="form.secteur" required :class="inputClass">
          <option value="" disabled>Choisir...</option>
          <option v-for="s in secteurs" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div>
        <label for="t-puiss" :class="labelClass">Puissance nominale (kVA)</label>
        <input id="t-puiss" v-model="form.puissance" type="number" step="any" min="0.1" required :class="inputClass" />
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="t-mt" :class="labelClass">Tension MT (kV)</label>
        <input id="t-mt" v-model="form.tension_mt" type="number" step="any" min="0.1" required :class="inputClass" />
      </div>
      <div>
        <label for="t-bt" :class="labelClass">Tension BT (V)</label>
        <input id="t-bt" v-model="form.tension_bt" type="number" step="any" min="1" required :class="inputClass" />
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="t-huile" :class="labelClass">Type d'huile diélectrique</label>
        <input id="t-huile" v-model="form.type_huile" maxlength="100" placeholder="Huile minérale" :class="inputClass" />
      </div>
      <div>
        <label for="t-niveau" :class="labelClass">Niveau d'huile</label>
        <select id="t-niveau" v-model="form.niveau_huile" :class="inputClass">
          <option v-for="(label, value) in NIVEAU_HUILE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div>
        <label for="t-date" :class="labelClass">Mise en service</label>
        <input id="t-date" v-model="form.date_installation" type="date" :class="inputClass" />
      </div>
      <div>
        <label for="t-etat" :class="labelClass">État technique</label>
        <select id="t-etat" v-model="form.etat" :class="inputClass">
          <option v-for="(label, value) in ETAT_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div>
        <label for="t-period" :class="labelClass">Périodicité (mois)</label>
        <input id="t-period" v-model="form.periodicite_inspection_mois" type="number" min="1" max="60" required :class="inputClass" />
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="t-lat" :class="labelClass">Latitude</label>
        <input id="t-lat" v-model="form.latitude" type="number" step="any" min="-90" max="90" required placeholder="-19.8659" :class="inputClass" />
      </div>
      <div>
        <label for="t-lng" :class="labelClass">Longitude</label>
        <input id="t-lng" v-model="form.longitude" type="number" step="any" min="-180" max="180" required placeholder="47.0333" :class="inputClass" />
      </div>
    </div>
    <p class="-mt-2 text-xs text-slate-500">
      Zone acceptée : latitude de -20.05 à -19.70, longitude de 46.90 à 47.20 (centre d'Antsirabe : -19.866 / 47.033).
    </p>

    <label class="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
      <input v-model="form.actif" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
      Transformateur actif
    </label>

    <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="btnSecondary" :disabled="saving" @click="emit('cancel')">Annuler</button>
      <button type="submit" :class="btnPrimary" :disabled="saving">
        {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
      </button>
    </div>
  </form>
</template>