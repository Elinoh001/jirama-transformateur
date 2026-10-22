<script setup>
import { reactive } from 'vue'

import { ROLE_LABELS } from '@/utils/format'
import { btnPrimary, btnSecondary, inputClass, labelClass } from '@/utils/ui'

const props = defineProps({
  utilisateur: { type: Object, default: null }, // null = création
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])

const u = props.utilisateur
const form = reactive({
  nom: u?.nom ?? '',
  prenom: u?.prenom ?? '',
  email: u?.email ?? '',
  mot_de_passe: '',
  role: u?.role ?? 'AGENT',
  actif: u?.actif ?? true,
})

function submit() {
  const payload = {
    nom: form.nom.trim(),
    prenom: form.prenom.trim(),
    email: form.email.trim(),
    role: form.role,
    actif: form.actif,
  }
  // En modification, un mot de passe vide = on ne change pas le mot de passe.
  if (form.mot_de_passe) payload.mot_de_passe = form.mot_de_passe
  emit('submit', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="u-nom" :class="labelClass">Nom</label>
        <input id="u-nom" v-model="form.nom" required maxlength="100" :class="inputClass" />
      </div>
      <div>
        <label for="u-prenom" :class="labelClass">Prénom</label>
        <input id="u-prenom" v-model="form.prenom" required maxlength="100" :class="inputClass" />
      </div>
    </div>

    <div>
      <label for="u-email" :class="labelClass">Email</label>
      <input id="u-email" v-model="form.email" type="email" required maxlength="255" :class="inputClass" />
    </div>

    <div>
      <label for="u-mdp" :class="labelClass">
        Mot de passe
        <span v-if="utilisateur" class="font-normal text-slate-400">(laisser vide pour ne pas changer)</span>
      </label>
      <input
        id="u-mdp"
        v-model="form.mot_de_passe"
        type="password"
        :required="!utilisateur"
        minlength="8"
        maxlength="72"
        autocomplete="new-password"
        placeholder="8 caractères minimum"
        :class="inputClass"
      />
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="u-role" :class="labelClass">Rôle</label>
        <select id="u-role" v-model="form.role" :class="inputClass">
          <option v-for="(label, value) in ROLE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <label class="mt-6 flex cursor-pointer items-center gap-2 text-sm text-slate-700">
        <input v-model="form.actif" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
        Compte actif
      </label>
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