<script setup>
import { computed, reactive } from 'vue'

import { STATUT_LABELS, TYPE_INTERVENTION_LABELS, todayISO } from '@/utils/format'
import { btnPrimary, btnSecondary, inputClass, labelClass } from '@/utils/ui'

const props = defineProps({
  intervention: { type: Object, default: null }, // null = création
  transformateurs: { type: Array, default: () => [] }, // [{ id, reference, nom }]
  lockedId: { type: Number, default: null }, // transformateur imposé (page de détail)
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])

const iv = props.intervention
const form = reactive({
  transformateur_id: iv?.transformateur_id ?? props.lockedId ?? '',
  date_intervention: iv?.date_intervention ?? todayISO(),
  type: iv?.type ?? 'PREVENTIVE',
  statut: iv?.statut ?? 'PLANIFIEE',
  cout: iv?.cout ?? '',
  description: iv?.description ?? '',
  technicien: iv?.technicien ?? '',
})

// Le transformateur d'une intervention existante ne peut pas être changé (règle du backend).
const verrouille = computed(() => !!props.intervention || props.lockedId !== null)

function submit() {
  const payload = {
    date_intervention: form.date_intervention,
    type: form.type,
    statut: form.statut,
    cout: form.cout === '' || form.cout === null ? null : Number(form.cout),
    description: form.description.trim() || null,
  }
  // Technicien vide : le backend utilise le nom de l'utilisateur connecté.
  if (form.technicien.trim()) payload.technicien = form.technicien.trim()
  if (!props.intervention) payload.transformateur_id = Number(form.transformateur_id)
  emit('submit', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
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
        <input id="v-date" v-model="form.date_intervention" type="date" required :class="inputClass" />
      </div>
      <div>
        <label for="v-type" :class="labelClass">Type</label>
        <select id="v-type" v-model="form.type" :class="inputClass">
          <option v-for="(label, value) in TYPE_INTERVENTION_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div>
        <label for="v-statut" :class="labelClass">Statut</label>
        <select id="v-statut" v-model="form.statut" :class="inputClass">
          <option v-for="(label, value) in STATUT_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="v-cout" :class="labelClass">Coût (Ar)</label>
        <input id="v-cout" v-model="form.cout" type="number" min="0" step="any" :class="inputClass" />
      </div>
      <div>
        <label for="v-tech" :class="labelClass">Technicien</label>
        <input
          id="v-tech"
          v-model="form.technicien"
          maxlength="150"
          placeholder="Laisser vide pour utiliser votre nom"
          :class="inputClass"
        />
      </div>
    </div>

    <div>
      <label for="v-desc" :class="labelClass">Description</label>
      <textarea id="v-desc" v-model="form.description" rows="3" maxlength="2000" :class="inputClass"></textarea>
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