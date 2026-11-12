<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { Pencil, Plus } from 'lucide-vue-next'

import AppModal from '@/components/common/AppModal.vue'
import BadgeGravite from '@/components/common/BadgeGravite.vue'
import BadgeStatutPanne from '@/components/common/BadgeStatutPanne.vue'
import PanneForm from '@/components/pannes/PanneForm.vue'
import PanneTraitementForm from '@/components/pannes/PanneTraitementForm.vue'
import panneService from '@/services/panneService'
import { getErrorMessage } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { GRAVITE_LABELS, STATUT_PANNE_LABELS, TYPE_PANNE_LABELS, formatDateTime, labelOf } from '@/utils/format'
import { btnIcon, btnPrimary, cardClass, inputClass, thClass } from '@/utils/ui'

const auth = useAuthStore()
const transformateurs = useTransformateurStore()

const pannes = ref([])
const loading = ref(false)
const error = ref('')

const filtreTransformateur = ref('')
const filtreStatut = ref('')
const filtreGravite = ref('')
const activesSeulement = ref(false)

const modal = ref(null) // 'creation' | 'traitement' | null
const editing = ref(null)
const saving = ref(false)
const formError = ref('')

const nbActives = computed(() => pannes.value.filter((p) => p.active).length)
const nbCritiques = computed(() => pannes.value.filter((p) => p.active && p.gravite === 'CRITIQUE').length)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filtreTransformateur.value) params.transformateur_id = filtreTransformateur.value
    if (filtreStatut.value) params.statut = filtreStatut.value
    if (filtreGravite.value) params.gravite = filtreGravite.value
    if (activesSeulement.value) params.active = true
    pannes.value = await panneService.list(params)
  } catch (e) {
    error.value = getErrorMessage(e, 'Impossible de charger les pannes')
  } finally {
    loading.value = false
  }
}

watch([filtreTransformateur, filtreStatut, filtreGravite, activesSeulement], load)
onMounted(() => {
  transformateurs.fetchAll()
  load()
})

function ouvrirCreation() {
  editing.value = null
  formError.value = ''
  modal.value = 'creation'
}

function ouvrirTraitement(panne) {
  editing.value = panne
  formError.value = ''
  modal.value = 'traitement'
}

async function enregistrer(action) {
  saving.value = true
  formError.value = ''
  try {
    await action()
    modal.value = null
    await load()
  } catch (e) {
    formError.value = getErrorMessage(e, "Impossible d'enregistrer la panne")
  } finally {
    saving.value = false
  }
}

const creer = (payload) => enregistrer(() => panneService.create(payload))
const traiter = (payload) => enregistrer(() => panneService.update(editing.value.id, payload))
</script>

<template>
  <div class="space-y-4">
    <div :class="[cardClass, 'flex flex-wrap items-end gap-4 p-4']">
      <div class="min-w-[220px]">
        <label for="f-trans" class="mb-1 block text-xs font-medium text-slate-500">Transformateur</label>
        <select id="f-trans" v-model="filtreTransformateur" :class="inputClass">
          <option value="">Tous</option>
          <option v-for="t in transformateurs.items" :key="t.id" :value="t.id">{{ t.reference }} — {{ t.nom }}</option>
        </select>
      </div>
      <div>
        <label for="f-statut" class="mb-1 block text-xs font-medium text-slate-500">Statut</label>
        <select id="f-statut" v-model="filtreStatut" :class="[inputClass, 'w-36']">
          <option value="">Tous</option>
          <option v-for="(label, value) in STATUT_PANNE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div>
        <label for="f-gravite" class="mb-1 block text-xs font-medium text-slate-500">Gravité</label>
        <select id="f-gravite" v-model="filtreGravite" :class="[inputClass, 'w-36']">
          <option value="">Toutes</option>
          <option v-for="(label, value) in GRAVITE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <label class="flex cursor-pointer items-center gap-2 pb-2 text-sm text-slate-700">
        <input v-model="activesSeulement" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
        Pannes actives uniquement
      </label>
      <button v-if="auth.canWriteTerrain" type="button" :class="[btnPrimary, 'ml-auto']" @click="ouvrirCreation">
        <Plus class="h-4 w-4" /> Signaler une panne
      </button>
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>

    <div :class="[cardClass, 'overflow-x-auto']">
      <table class="min-w-full text-sm">
        <thead class="border-b border-slate-200 bg-slate-50">
          <tr>
            <th :class="thClass">Signalée le</th>
            <th :class="thClass">Transformateur</th>
            <th :class="thClass">Type</th>
            <th :class="thClass">Gravité</th>
            <th :class="thClass">Statut</th>
            <th :class="thClass">Description</th>
            <th :class="thClass">Actions correctives</th>
            <th v-if="auth.canWriteTerrain" :class="[thClass, 'text-right']">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="loading && pannes.length === 0">
            <td colspan="8" class="px-3 py-8 text-center text-slate-500">Chargement...</td>
          </tr>
          <tr v-else-if="pannes.length === 0">
            <td colspan="8" class="px-3 py-8 text-center text-slate-500">Aucune panne trouvée.</td>
          </tr>
          <tr v-for="p in pannes" :key="p.id" class="align-top hover:bg-slate-50">
            <td class="whitespace-nowrap px-3 py-3">
              {{ formatDateTime(p.date_signalement) }}
              <span class="block text-xs text-slate-500">par {{ p.signale_par }}</span>
            </td>
            <td class="px-3 py-3">
              <RouterLink :to="`/transformateurs/${p.transformateur_id}`" class="font-medium text-blue-600 hover:underline">
                {{ p.transformateur_reference }}
              </RouterLink>
              <span class="block text-xs text-slate-500">{{ p.transformateur_nom }}</span>
            </td>
            <td class="px-3 py-3">{{ labelOf(TYPE_PANNE_LABELS, p.type_panne) }}</td>
            <td class="px-3 py-3"><BadgeGravite :gravite="p.gravite" /></td>
            <td class="px-3 py-3">
              <BadgeStatutPanne :statut="p.statut" />
              <span v-if="p.date_resolution" class="mt-1 block text-xs text-slate-500">
                le {{ formatDateTime(p.date_resolution) }}
              </span>
            </td>
            <td class="max-w-xs px-3 py-3 text-slate-600">{{ p.description }}</td>
            <td class="max-w-xs px-3 py-3 text-slate-600">{{ p.actions_correctives || '—' }}</td>
            <td v-if="auth.canWriteTerrain" class="whitespace-nowrap px-3 py-3 text-right">
              <button
                v-if="p.active"
                type="button"
                :class="btnIcon"
                title="Traiter ou résoudre"
                @click="ouvrirTraitement(p)"
              >
                <Pencil class="h-4 w-4" />
              </button>
              <span v-else class="text-xs text-slate-400">Clôturée</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="text-xs text-slate-500">
      {{ pannes.length }} panne(s) affichée(s) · {{ nbActives }} active(s), dont {{ nbCritiques }} critique(s)
    </p>

    <AppModal :open="modal === 'creation'" title="Signaler une panne" wide @close="modal = null">
      <PanneForm
        :transformateurs="transformateurs.items"
        :saving="saving"
        :error="formError"
        @submit="creer"
        @cancel="modal = null"
      />
    </AppModal>

    <AppModal
      :open="modal === 'traitement'"
      :title="editing ? `Traitement de la panne · ${editing.transformateur_reference}` : ''"
      wide
      @close="modal = null"
    >
      <PanneTraitementForm
        v-if="editing && modal === 'traitement'"
        :panne="editing"
        :saving="saving"
        :error="formError"
        @submit="traiter"
        @cancel="modal = null"
      />
    </AppModal>
  </div>
</template>
