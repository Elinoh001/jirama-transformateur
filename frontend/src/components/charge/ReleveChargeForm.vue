<script setup>
import { computed, reactive } from 'vue'

import { formatPourcent, todayISO } from '@/utils/format'
import { btnPrimary, btnSecondary, inputClass, labelClass } from '@/utils/ui'

const props = defineProps({
  // [{ id, reference, nom, puissance, tension_bt }] : nécessaires à l'estimation du taux
  transformateurs: { type: Array, default: () => [] },
  lockedId: { type: Number, default: null },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  transformateur_id: props.lockedId ?? '',
  date_releve: todayISO(),
  mode: 'puissance', // 'puissance' (kVA) ou 'courant' (A)
  valeur: '',
  releve_par: '',
})

const maxDate = todayISO()

const transformateur = computed(
  () => props.transformateurs.find((t) => t.id === Number(form.transformateur_id)) ?? null,
)

// Même calcul que le backend : avec le courant, S = racine(3) x U x I / 1000.
const puissanceEstimee = computed(() => {
  const v = Number(form.valeur)
  if (!transformateur.value || form.valeur === '' || Number.isNaN(v) || v < 0) return null
  if (form.mode === 'puissance') return v
  return (Math.sqrt(3) * transformateur.value.tension_bt * v) / 1000
})

const tauxEstime = computed(() => {
  if (puissanceEstimee.value === null) return null
  return (puissanceEstimee.value / transformateur.value.puissance) * 100
})

function submit() {
  const payload = {
    transformateur_id: Number(form.transformateur_id),
    date_releve: form.date_releve,
  }
  if (form.mode === 'puissance') payload.puissance_mesuree = Number(form.valeur)
  else payload.courant_mesure = Number(form.valeur)
  // Vide : le backend utilise le nom de l'utilisateur connecté.
  if (form.releve_par.trim()) payload.releve_par = form.releve_par.trim()
  emit('submit', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div>
      <label for="r-trans" :class="labelClass">Transformateur</label>
      <select id="r-trans" v-model="form.transformateur_id" required :disabled="lockedId !== null" :class="inputClass">
        <option value="" disabled>Choisir...</option>
        <option v-for="t in transformateurs" :key="t.id" :value="t.id">
          {{ t.reference }} — {{ t.nom }} ({{ t.puissance }} kVA)
        </option>
      </select>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div>
        <label for="r-date" :class="labelClass">Date du relevé</label>
        <input id="r-date" v-model="form.date_releve" type="date" :max="maxDate" required :class="inputClass" />
      </div>
      <div>
        <label for="r-mode" :class="labelClass">Mesure</label>
        <select id="r-mode" v-model="form.mode" :class="inputClass">
          <option value="puissance">Puissance (kVA)</option>
          <option value="courant">Courant (A)</option>
        </select>
      </div>
      <div>
        <label for="r-valeur" :class="labelClass">{{ form.mode === 'puissance' ? 'Puissance (kVA)' : 'Courant (A)' }}</label>
        <input id="r-valeur" v-model="form.valeur" type="number" step="any" min="0" required :class="inputClass" />
      </div>
    </div>

    <div
      v-if="tauxEstime !== null"
      class="rounded-lg px-3 py-2 text-sm"
      :class="tauxEstime > 100 ? 'bg-orange-50 text-orange-800' : 'bg-green-50 text-green-800'"
    >
      Taux de charge estimé : <strong>{{ formatPourcent(tauxEstime) }}</strong>
      <span v-if="form.mode === 'courant'"> (puissance estimée : {{ puissanceEstimee.toFixed(1) }} kVA)</span>
      <span v-if="tauxEstime > 100"> : le poste sera en surcharge.</span>
    </div>

    <div>
      <label for="r-par" :class="labelClass">Relevé par</label>
      <input
        id="r-par"
        v-model="form.releve_par"
        maxlength="150"
        placeholder="Laisser vide pour utiliser votre nom"
        :class="inputClass"
      />
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="btnSecondary" :disabled="saving" @click="emit('cancel')">Annuler</button>
      <button type="submit" :class="btnPrimary" :disabled="saving">
        {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
      </button>
    </div>
  </form>
</template>