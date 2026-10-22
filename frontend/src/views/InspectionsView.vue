<script setup>
import { onMounted, ref, watch } from 'vue'
import { Pencil, Plus } from 'lucide-vue-next'

import AppModal from '@/components/common/AppModal.vue'
import BadgeEtat from '@/components/common/BadgeEtat.vue'
import InspectionForm from '@/components/inspections/InspectionForm.vue'
import inspectionService from '@/services/inspectionService'
import { getErrorMessage } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { TYPE_INSPECTION_LABELS, formatDate, labelOf } from '@/utils/format'
import { btnIcon, btnPrimary, cardClass, inputClass, thClass } from '@/utils/ui'

const auth = useAuthStore()
const transformateurs = useTransformateurStore()

const inspections = ref([])
const loading = ref(false)
const error = ref('')

const filtreTransformateur = ref('')
const filtreEtat = ref('')

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
    if (filtreEtat.value) params.etat = filtreEtat.value
    inspections.value = await inspectionService.list(params)
  } catch (e) {
    error.value = getErrorMessage(e, 'Impossible de charger les inspections')
  } finally {
    loading.value = false
  }
}

watch([filtreTransformateur, filtreEtat], load)
onMounted(() => {
  transformateurs.fetchAll()
  load()
})

function ouvrirCreation() {
  editing.value = null
  formError.value = ''
  showForm.value = true
}

function ouvrirEdition(inspection) {
  editing.value = inspection
  formError.value = ''
  showForm.value = true
}

async function enregistrer(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await inspectionService.update(editing.value.id, payload)
    } else {
      await inspectionService.create(payload)
    }
    showForm.value = false
    await load()
  } catch (e) {
    formError.value = getErrorMessage(e, "Impossible d'enregistrer l'inspection")
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
        <label for="f-etat" class="mb-1 block text-xs font-medium text-slate-500">État constaté</label>
        <select id="f-etat" v-model="filtreEtat" :class="[inputClass, 'w-40']">
          <option value="">Tous</option>
          <option value="BON">Bon</option>
          <option value="A_SURVEILLER">À surveiller</option>
          <option value="CRITIQUE">Critique</option>
        </select>
      </div>
      <button v-if="auth.canWriteTerrain" type="button" :class="[btnPrimary, 'ml-auto']" @click="ouvrirCreation">
        <Plus class="h-4 w-4" /> Nouvelle inspection
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
            <th :class="thClass">État</th>
            <th :class="thClass">Observation</th>
            <th :class="thClass">Technicien</th>
            <th v-if="auth.canWriteTerrain" :class="[thClass, 'text-right']">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="loading && inspections.length === 0">
            <td colspan="7" class="px-3 py-8 text-center text-slate-500">Chargement...</td>
          </tr>
          <tr v-else-if="inspections.length === 0">
            <td colspan="7" class="px-3 py-8 text-center text-slate-500">Aucune inspection trouvée.</td>
          </tr>
          <tr v-for="i in inspections" :key="i.id" class="align-top hover:bg-slate-50">
            <td class="whitespace-nowrap px-3 py-3">{{ formatDate(i.date_inspection) }}</td>
            <td class="px-3 py-3">
              <RouterLink :to="`/transformateurs/${i.transformateur_id}`" class="font-medium text-blue-600 hover:underline">
                {{ i.transformateur_reference }}
              </RouterLink>
              <span class="block text-xs text-slate-500">{{ i.transformateur_nom }}</span>
            </td>
            <td class="px-3 py-3">{{ labelOf(TYPE_INSPECTION_LABELS, i.type) }}</td>
            <td class="px-3 py-3"><BadgeEtat :etat="i.etat" /></td>
            <td class="max-w-xs px-3 py-3 text-slate-600">{{ i.observation || '—' }}</td>
            <td class="whitespace-nowrap px-3 py-3">{{ i.technicien }}</td>
            <td v-if="auth.canWriteTerrain" class="whitespace-nowrap px-3 py-3 text-right">
              <button type="button" :class="btnIcon" title="Modifier" @click="ouvrirEdition(i)">
                <Pencil class="h-4 w-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="text-xs text-slate-500">{{ inspections.length }} inspection(s)</p>

    <AppModal
      :open="showForm"
      :title="editing ? `Modifier l'inspection du ${formatDate(editing.date_inspection)}` : 'Nouvelle inspection'"
      wide
      @close="showForm = false"
    >
      <InspectionForm
        :inspection="editing"
        :transformateurs="transformateurs.items"
        :saving="saving"
        :error="formError"
        @submit="enregistrer"
        @cancel="showForm = false"
      />
    </AppModal>
  </div>
</template>