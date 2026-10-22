<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Eye, Pencil, Plus, Search, Trash2 } from 'lucide-vue-next'

import AppModal from '@/components/common/AppModal.vue'
import BadgeEtat from '@/components/common/BadgeEtat.vue'
import BadgePriorite from '@/components/common/BadgePriorite.vue'
import BadgeStatutOperationnel from '@/components/common/BadgeStatutOperationnel.vue'
import TauxCharge from '@/components/common/TauxCharge.vue'
import TransformateurForm from '@/components/transformateurs/TransformateurForm.vue'
import { getErrorMessage } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { STATUT_OPERATIONNEL_LABELS, formatDate } from '@/utils/format'
import { btnIcon, btnIconDanger, btnPrimary, cardClass, inputClass, thClass } from '@/utils/ui'

const auth = useAuthStore()
const store = useTransformateurStore()

const search = ref('')
const secteur = ref('')
const statutOp = ref('')
const etat = ref('')
const actif = ref('')
const niveau = ref('')

const showForm = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')
const pageError = ref('')

function buildParams() {
  const p = {}
  if (search.value.trim()) p.search = search.value.trim()
  if (secteur.value) p.secteur = secteur.value
  if (statutOp.value) p.statut_operationnel = statutOp.value
  if (etat.value) p.etat = etat.value
  if (actif.value !== '') p.actif = actif.value === 'true'
  return p
}

function load() {
  return store.fetchAll(buildParams())
}

// La priorité est calculée côté backend : on filtre ici sur le résultat.
const lignes = computed(() =>
  niveau.value ? store.items.filter((t) => t.priorite === niveau.value) : store.items,
)

let timer = null
watch(search, () => {
  clearTimeout(timer)
  timer = setTimeout(load, 300)
})
watch([secteur, statutOp, etat, actif], load)
onBeforeUnmount(() => clearTimeout(timer))
onMounted(() => {
  store.fetchSecteurs()
  load()
})

function ouvrirCreation() {
  editing.value = null
  formError.value = ''
  showForm.value = true
}

function ouvrirEdition(t) {
  editing.value = t
  formError.value = ''
  showForm.value = true
}

async function enregistrer(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await store.update(editing.value.id, payload)
    } else {
      await store.create(payload)
    }
    showForm.value = false
  } catch (e) {
    formError.value = getErrorMessage(e, "Impossible d'enregistrer le transformateur")
  } finally {
    saving.value = false
  }
}

async function supprimer(t) {
  const ok = window.confirm(
    `Supprimer le transformateur ${t.reference} ?\nSes inspections, interventions, relevés et pannes seront aussi supprimés.`,
  )
  if (!ok) return
  pageError.value = ''
  try {
    await store.remove(t.id)
  } catch (e) {
    pageError.value = getErrorMessage(e, 'Suppression impossible')
  }
}
</script>

<template>
  <div class="space-y-4">
    <div :class="[cardClass, 'flex flex-wrap items-end gap-4 p-4']">
      <div class="min-w-[220px] flex-1">
        <label for="search" class="mb-1 block text-xs font-medium text-slate-500">Recherche</label>
        <div class="relative">
          <Search class="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            id="search"
            v-model="search"
            placeholder="Référence, nom ou quartier"
            :class="[inputClass, 'pl-9']"
          />
        </div>
      </div>

      <div>
        <label for="f-secteur" class="mb-1 block text-xs font-medium text-slate-500">Quartier</label>
        <select id="f-secteur" v-model="secteur" :class="[inputClass, 'w-44']">
          <option value="">Tous</option>
          <option v-for="s in store.secteurs" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>

      <div>
        <label for="f-statutop" class="mb-1 block text-xs font-medium text-slate-500">Statut</label>
        <select id="f-statutop" v-model="statutOp" :class="[inputClass, 'w-44']">
          <option value="">Tous</option>
          <option v-for="(label, value) in STATUT_OPERATIONNEL_LABELS" :key="value" :value="value">
            {{ label }}
          </option>
        </select>
      </div>

      <div>
        <label for="f-etat" class="mb-1 block text-xs font-medium text-slate-500">État technique</label>
        <select id="f-etat" v-model="etat" :class="[inputClass, 'w-40']">
          <option value="">Tous</option>
          <option value="BON">Bon</option>
          <option value="A_SURVEILLER">À surveiller</option>
          <option value="CRITIQUE">Critique</option>
        </select>
      </div>

      <div>
        <label for="f-niveau" class="mb-1 block text-xs font-medium text-slate-500">Priorité</label>
        <select id="f-niveau" v-model="niveau" :class="[inputClass, 'w-40']">
          <option value="">Toutes</option>
          <option value="PRIORITAIRE">Prioritaire</option>
          <option value="A_SURVEILLER">À surveiller</option>
          <option value="NORMAL">Normal</option>
        </select>
      </div>

      <div>
        <label for="f-actif" class="mb-1 block text-xs font-medium text-slate-500">Activité</label>
        <select id="f-actif" v-model="actif" :class="[inputClass, 'w-32']">
          <option value="">Tous</option>
          <option value="true">Actifs</option>
          <option value="false">Inactifs</option>
        </select>
      </div>

      <button v-if="auth.canManageTransformateurs" type="button" :class="btnPrimary" @click="ouvrirCreation">
        <Plus class="h-4 w-4" /> Nouveau
      </button>
    </div>

    <p v-if="store.error || pageError" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ store.error || pageError }}
    </p>

    <div :class="[cardClass, 'overflow-x-auto']">
      <table class="min-w-full text-sm">
        <thead class="border-b border-slate-200 bg-slate-50">
          <tr>
            <th :class="thClass">Référence</th>
            <th :class="thClass">Nom</th>
            <th :class="thClass">Quartier</th>
            <th :class="thClass">Puissance</th>
            <th :class="thClass">Statut</th>
            <th :class="thClass">Charge</th>
            <th :class="thClass">État technique</th>
            <th :class="thClass">Priorité</th>
            <th :class="thClass">Prochaine inspection</th>
            <th :class="[thClass, 'text-right']">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="store.loading && lignes.length === 0">
            <td colspan="10" class="px-3 py-8 text-center text-slate-500">Chargement...</td>
          </tr>
          <tr v-else-if="lignes.length === 0">
            <td colspan="10" class="px-3 py-8 text-center text-slate-500">Aucun transformateur trouvé.</td>
          </tr>
          <tr v-for="t in lignes" :key="t.id" class="hover:bg-slate-50">
            <td class="whitespace-nowrap px-3 py-3 font-medium">
              <RouterLink :to="`/transformateurs/${t.id}`" class="text-blue-600 hover:underline">
                {{ t.reference }}
              </RouterLink>
              <span v-if="!t.actif" class="ml-2 rounded bg-slate-200 px-1.5 py-0.5 text-xs font-normal text-slate-500">
                Inactif
              </span>
            </td>
            <td class="px-3 py-3">{{ t.nom }}</td>
            <td class="whitespace-nowrap px-3 py-3 text-slate-600">{{ t.secteur }}</td>
            <td class="whitespace-nowrap px-3 py-3">{{ t.puissance }} kVA</td>
            <td class="px-3 py-3"><BadgeStatutOperationnel :statut="t.statut_operationnel" /></td>
            <td class="px-3 py-3"><TauxCharge :taux="t.taux_charge" /></td>
            <td class="px-3 py-3"><BadgeEtat :etat="t.etat" /></td>
            <td class="px-3 py-3"><BadgePriorite :niveau="t.priorite" /></td>
            <td
              class="whitespace-nowrap px-3 py-3"
              :class="t.actif && t.prochaine_inspection && t.prochaine_inspection < new Date().toISOString().slice(0, 10) ? 'font-semibold text-red-700' : 'text-slate-600'"
            >
              {{ formatDate(t.prochaine_inspection) }}
            </td>
            <td class="whitespace-nowrap px-3 py-3 text-right">
              <RouterLink :to="`/transformateurs/${t.id}`" :class="btnIcon" title="Détail">
                <Eye class="h-4 w-4" />
              </RouterLink>
              <template v-if="auth.canManageTransformateurs">
                <button type="button" :class="btnIcon" title="Modifier" @click="ouvrirEdition(t)">
                  <Pencil class="h-4 w-4" />
                </button>
                <button type="button" :class="btnIconDanger" title="Supprimer" @click="supprimer(t)">
                  <Trash2 class="h-4 w-4" />
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="text-xs text-slate-500">{{ lignes.length }} transformateur(s) affiché(s)</p>

    <AppModal
      :open="showForm"
      :title="editing ? `Modifier ${editing.reference}` : 'Nouveau transformateur'"
      wide
      @close="showForm = false"
    >
      <TransformateurForm
        :transformateur="editing"
        :secteurs="store.secteurs"
        :saving="saving"
        :error="formError"
        @submit="enregistrer"
        @cancel="showForm = false"
      />
    </AppModal>
  </div>
</template>