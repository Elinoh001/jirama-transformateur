<script setup>
import { onMounted, ref, watch } from 'vue'
import { Eye, Pencil, Plus } from 'lucide-vue-next'

import AppModal from '@/components/common/AppModal.vue'
import BadgeStatut from '@/components/common/BadgeStatut.vue'
import BadgeTag from '@/components/common/BadgeTag.vue'
import InterventionForm from '@/components/interventions/InterventionForm.vue'
import interventionService from '@/services/interventionService'
import { getErrorMessage } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { STATUT_LABELS, TYPE_INTERVENTION_LABELS, formatDate, formatMontant, labelOf } from '@/utils/format'
import { btnIcon, btnPrimary, cardClass, inputClass, thClass } from '@/utils/ui'

const auth = useAuthStore()
const transformateurs = useTransformateurStore()

const interventions = ref([])
const loading = ref(false)
const error = ref('')

const filtreTransformateur = ref('')
const filtreStatut = ref('')
const filtreRetard = ref(false)

const showForm = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filtreTransformateur.value) params.transformateur_id = filtreTransformateur.value
    if (filtreStatut.value) params.statut = filtreStatut.value
    if (filtreRetard.value) params.en_retard = true
    interventions.value = await interventionService.list(params)
  } catch (e) {
    error.value = getErrorMessage(e, 'Impossible de charger les interventions')
  } finally {
    loading.value = false
  }
}

watch([filtreTransformateur, filtreStatut, filtreRetard], load)
onMounted(() => {
  transformateurs.fetchAll()
  load()
})

function titreAction(iv) {
  if (iv.statut === 'ANNULEE') return 'Consulter (archivée)'
  if (iv.statut === 'TERMINEE') return 'Compléter le compte-rendu ou le coût'
  return 'Modifier'
}

function ouvrirCreation() {
  editing.value = null
  formError.value = ''
  showForm.value = true
}

function ouvrirEdition(intervention) {
  editing.value = intervention
  formError.value = ''
  showForm.value = true
}

async function enregistrer(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await interventionService.update(editing.value.id, payload)
    } else {
      await interventionService.create(payload)
    }
    showForm.value = false
    await load()
  } catch (e) {
    formError.value = getErrorMessage(e, "Impossible d'enregistrer l'intervention")
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div :class="[cardClass, 'flex flex-wrap items-end gap-4 p-4']">
      <div class="min-w-[220px]">
        <label for="f-trans" class="mb-1 block text-xs font-medium text-slate-500">Transformateur</label>
        <select id="f-trans" v-model="filtreTransformateur" :class="inputClass">
          <option value="">Tous</option>
          <option v-for="t in transformateurs.items" :key="t.id" :value="t.id">
            {{ t.reference }} — {{ t.nom }}
          </option>
        </select>
      </div>
      <div>
        <label for="f-statut" class="mb-1 block text-xs font-medium text-slate-500">Statut</label>
        <select id="f-statut" v-model="filtreStatut" :class="[inputClass, 'w-40']">
          <option value="">Tous</option>
          <option v-for="(label, value) in STATUT_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <label class="flex cursor-pointer items-center gap-2 pb-2 text-sm text-slate-700">
        <input v-model="filtreRetard" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
        En retard uniquement
      </label>
      <button v-if="auth.canWriteTerrain" type="button" :class="[btnPrimary, 'ml-auto']" @click="ouvrirCreation">
        <Plus class="h-4 w-4" /> Nouvelle intervention
      </button>
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>

    <div :class="[cardClass, 'overflow-x-auto']">
      <table class="min-w-full text-sm">
        <thead class="border-b border-slate-200 bg-slate-50">
          <tr>
            <th :class="thClass">Date</th>
            <th :class="thClass">Transformateur</th>
            <th :class="thClass">Type</th>
            <th :class="thClass">Statut</th>
            <th :class="thClass">Coût</th>
            <th :class="thClass">Description / compte-rendu</th>
            <th :class="thClass">Technicien</th>
            <th v-if="auth.canWriteTerrain" :class="[thClass, 'text-right']">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="loading && interventions.length === 0">
            <td colspan="8" class="px-3 py-8 text-center text-slate-500">Chargement...</td>
          </tr>
          <tr v-else-if="interventions.length === 0">
            <td colspan="8" class="px-3 py-8 text-center text-slate-500">Aucune intervention trouvée.</td>
          </tr>
          <tr v-for="iv in interventions" :key="iv.id" class="align-top hover:bg-slate-50">
            <td class="whitespace-nowrap px-3 py-3">{{ formatDate(iv.date_intervention) }}</td>
            <td class="px-3 py-3">
              <RouterLink :to="`/transformateurs/${iv.transformateur_id}`" class="font-medium text-blue-600 hover:underline">
                {{ iv.transformateur_reference }}
              </RouterLink>
              <span class="block text-xs text-slate-500">{{ iv.transformateur_nom }}</span>
            </td>
            <td class="px-3 py-3">{{ labelOf(TYPE_INTERVENTION_LABELS, iv.type) }}</td>
            <td class="px-3 py-3">
              <BadgeStatut :statut="iv.statut" />
              <span v-if="iv.en_retard" class="mt-1 block">
                <BadgeTag tone="red" :label="`En retard de ${iv.jours_retard} j`" />
              </span>
            </td>
            <td class="whitespace-nowrap px-3 py-3">{{ iv.cout ? formatMontant(iv.cout) : '—' }}</td>
            <td class="max-w-xs px-3 py-3 text-slate-600">{{ iv.description || '—' }}</td>
            <td class="whitespace-nowrap px-3 py-3">{{ iv.technicien }}</td>
            <td v-if="auth.canWriteTerrain" class="whitespace-nowrap px-3 py-3 text-right">
              <button type="button" :class="btnIcon" :title="titreAction(iv)" @click="ouvrirEdition(iv)">
                <Eye v-if="iv.statut === 'ANNULEE'" class="h-4 w-4" />
                <Pencil v-else class="h-4 w-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="text-xs text-slate-500">{{ interventions.length }} intervention(s)</p>

    <AppModal
      :open="showForm"
      :title="editing ? `Intervention du ${formatDate(editing.date_intervention)}` : 'Nouvelle intervention'"
      wide
      @close="showForm = false"
    >
      <InterventionForm
        :intervention="editing"
        :transformateurs="transformateurs.items"
        :saving="saving"
        :error="formError"
        @submit="enregistrer"
        @cancel="showForm = false"
      />
    </AppModal>
  </div>
</template>
