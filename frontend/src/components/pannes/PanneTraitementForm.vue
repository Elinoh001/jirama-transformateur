<script setup>
import { computed, reactive } from 'vue'

import { GRAVITE_LABELS, STATUT_PANNE_LABELS } from '@/utils/format'
import { btnPrimary, btnSecondary, inputClass, labelClass } from '@/utils/ui'

const props = defineProps({
  panne: { type: Object, required: true },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])

const p = props.panne
const form = reactive({
  statut: p.statut,
  gravite: p.gravite,
  description: p.description,
  actions_correctives: p.actions_correctives ?? '',
})

// Transitions autorisées par le backend : SIGNALEE -> EN_COURS -> RESOLUE (ou SIGNALEE -> RESOLUE).
const statutsPossibles = computed(() =>
  p.statut === 'SIGNALEE' ? ['SIGNALEE', 'EN_COURS', 'RESOLUE'] : ['EN_COURS', 'RESOLUE'],
)
const resolution = computed(() => form.statut === 'RESOLUE')

function submit() {
  const payload = {
    statut: form.statut,
    gravite: form.gravite,
    description: form.description.trim(),
  }
  const actions = form.actions_correctives.trim()
  if (actions) payload.actions_correctives = actions
  emit('submit', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <p class="text-sm text-slate-600">
      <span class="font-semibold">{{ p.transformateur_reference }}</span> — {{ p.transformateur_nom }}
    </p>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="pt-statut" :class="labelClass">Statut</label>
        <select id="pt-statut" v-model="form.statut" :class="inputClass">
          <option v-for="s in statutsPossibles" :key="s" :value="s">{{ STATUT_PANNE_LABELS[s] }}</option>
        </select>
      </div>
      <div>
        <label for="pt-gravite" :class="labelClass">Gravité</label>
        <select id="pt-gravite" v-model="form.gravite" :class="inputClass">
          <option v-for="(label, value) in GRAVITE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
    </div>

    <div>
      <label for="pt-desc" :class="labelClass">Description</label>
      <textarea id="pt-desc" v-model="form.description" required minlength="3" maxlength="2000" rows="3" :class="inputClass"></textarea>
    </div>

    <div>
      <label for="pt-actions" :class="labelClass">
        Actions correctives
        <span v-if="resolution" class="font-normal text-red-600">(obligatoires pour résoudre)</span>
      </label>
      <textarea
        id="pt-actions"
        v-model="form.actions_correctives"
        :required="resolution"
        maxlength="2000"
        rows="3"
        :class="inputClass"
      ></textarea>
    </div>

    <p v-if="resolution" class="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">
      Une panne résolue ne peut plus être modifiée. S'il ne reste aucune autre panne critique active, le poste
      repasse « en service ».
    </p>

    <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="btnSecondary" :disabled="saving" @click="emit('cancel')">Annuler</button>
      <button type="submit" :class="btnPrimary" :disabled="saving">
        {{ saving ? 'Enregistrement...' : resolution ? 'Clôturer la panne' : 'Enregistrer' }}
      </button>
    </div>
  </form>
</template>