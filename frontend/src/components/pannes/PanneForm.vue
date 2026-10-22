<script setup>
import { reactive } from 'vue'

import { GRAVITE_LABELS, TYPE_PANNE_LABELS } from '@/utils/format'
import { btnPrimary, btnSecondary, inputClass, labelClass } from '@/utils/ui'

const props = defineProps({
  transformateurs: { type: Array, default: () => [] }, // [{ id, reference, nom }]
  lockedId: { type: Number, default: null }, // transformateur imposé (page de détail)
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  transformateur_id: props.lockedId ?? '',
  type_panne: 'FUITE_HUILE',
  gravite: 'MAJEURE',
  description: '',
})

function submit() {
  emit('submit', {
    transformateur_id: Number(form.transformateur_id),
    type_panne: form.type_panne,
    gravite: form.gravite,
    description: form.description.trim(),
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div>
      <label for="p-trans" :class="labelClass">Transformateur concerné</label>
      <select id="p-trans" v-model="form.transformateur_id" required :disabled="lockedId !== null" :class="inputClass">
        <option value="" disabled>Choisir...</option>
        <option v-for="t in transformateurs" :key="t.id" :value="t.id">{{ t.reference }} — {{ t.nom }}</option>
      </select>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="p-type" :class="labelClass">Type d'anomalie</label>
        <select id="p-type" v-model="form.type_panne" :class="inputClass">
          <option v-for="(label, value) in TYPE_PANNE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div>
        <label for="p-gravite" :class="labelClass">Niveau de gravité</label>
        <select id="p-gravite" v-model="form.gravite" :class="inputClass">
          <option v-for="(label, value) in GRAVITE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
    </div>

    <p v-if="form.gravite === 'CRITIQUE'" class="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-800">
      Une panne critique met immédiatement le poste « en panne » sur la carte et sur sa fiche.
    </p>

    <div>
      <label for="p-desc" :class="labelClass">Description</label>
      <textarea id="p-desc" v-model="form.description" required minlength="3" maxlength="2000" rows="4" :class="inputClass"></textarea>
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="btnSecondary" :disabled="saving" @click="emit('cancel')">Annuler</button>
      <button type="submit" :class="btnPrimary" :disabled="saving">
        {{ saving ? 'Enregistrement...' : 'Signaler la panne' }}
      </button>
    </div>
  </form>
</template>