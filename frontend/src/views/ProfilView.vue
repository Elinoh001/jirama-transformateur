<script setup>
import { computed, reactive, ref } from 'vue'

import authService from '@/services/authService'
import { getErrorMessage } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { ROLE_LABELS, labelOf } from '@/utils/format'
import { btnPrimary, cardClass, inputClass, labelClass } from '@/utils/ui'

const auth = useAuthStore()

const form = reactive({ ancien: '', nouveau: '', confirmation: '' })
const saving = ref(false)
const error = ref('')
const succes = ref('')

// Mêmes règles que le backend : 8 caractères minimum, au moins une lettre et un chiffre.
const regles = computed(() => [
  { texte: '8 caractères minimum', ok: form.nouveau.length >= 8 },
  { texte: 'Au moins une lettre', ok: /[A-Za-zÀ-ÿ]/.test(form.nouveau) },
  { texte: 'Au moins un chiffre', ok: /\d/.test(form.nouveau) },
  { texte: 'Différent de l’ancien', ok: form.nouveau !== '' && form.nouveau !== form.ancien },
])
const confirmationOk = computed(() => form.confirmation !== '' && form.confirmation === form.nouveau)
const valide = computed(() => regles.value.every((r) => r.ok) && confirmationOk.value && form.ancien !== '')

async function submit() {
  error.value = ''
  succes.value = ''
  if (!valide.value) return
  saving.value = true
  try {
    const res = await authService.changePassword(form.ancien, form.nouveau)
    succes.value = res.message || 'Mot de passe modifié avec succès.'
    form.ancien = ''
    form.nouveau = ''
    form.confirmation = ''
  } catch (e) {
    error.value = getErrorMessage(e, 'Impossible de modifier le mot de passe')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-6">
    <section :class="[cardClass, 'p-5']">
      <h3 class="mb-4 text-sm font-semibold text-slate-700">Mon compte</h3>
      <dl class="space-y-3 text-sm">
        <div class="flex justify-between gap-4">
          <dt class="text-slate-500">Nom</dt>
          <dd class="font-medium">{{ auth.fullName || '—' }}</dd>
        </div>
        <div class="flex justify-between gap-4">
          <dt class="text-slate-500">Adresse e-mail</dt>
          <dd class="font-medium">{{ auth.user?.email || '—' }}</dd>
        </div>
        <div class="flex justify-between gap-4">
          <dt class="text-slate-500">Rôle</dt>
          <dd class="font-medium">{{ labelOf(ROLE_LABELS, auth.role) }}</dd>
        </div>
      </dl>
    </section>

    <section :class="[cardClass, 'p-5']">
      <h3 class="mb-4 text-sm font-semibold text-slate-700">Changer mon mot de passe</h3>
      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label for="mdp-ancien" :class="labelClass">Mot de passe actuel</label>
          <input
            id="mdp-ancien"
            v-model="form.ancien"
            type="password"
            autocomplete="current-password"
            required
            :class="inputClass"
          />
        </div>
        <div>
          <label for="mdp-nouveau" :class="labelClass">Nouveau mot de passe</label>
          <input
            id="mdp-nouveau"
            v-model="form.nouveau"
            type="password"
            autocomplete="new-password"
            minlength="8"
            maxlength="72"
            required
            :class="inputClass"
          />
          <ul class="mt-2 grid grid-cols-1 gap-1 text-xs sm:grid-cols-2">
            <li v-for="r in regles" :key="r.texte" :class="r.ok ? 'text-green-700' : 'text-slate-500'">
              {{ r.ok ? '✓' : '○' }} {{ r.texte }}
            </li>
          </ul>
        </div>
        <div>
          <label for="mdp-confirmation" :class="labelClass">Confirmer le nouveau mot de passe</label>
          <input
            id="mdp-confirmation"
            v-model="form.confirmation"
            type="password"
            autocomplete="new-password"
            required
            :class="inputClass"
          />
          <p v-if="form.confirmation && !confirmationOk" class="mt-1 text-xs text-red-600">
            Les deux mots de passe ne correspondent pas.
          </p>
        </div>

        <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
        <p v-if="succes" class="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">{{ succes }}</p>

        <div class="flex justify-end">
          <button type="submit" :class="btnPrimary" :disabled="saving || !valide">
            {{ saving ? 'Enregistrement...' : 'Modifier le mot de passe' }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>
