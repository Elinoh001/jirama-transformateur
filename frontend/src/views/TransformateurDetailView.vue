<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ArrowLeft, ClipboardCheck, Gauge, Pencil, ShieldAlert, Trash2, Wrench } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'

import AppModal from '@/components/common/AppModal.vue'
import BadgeEtat from '@/components/common/BadgeEtat.vue'
import BadgePriorite from '@/components/common/BadgePriorite.vue'
import BadgeStatutOperationnel from '@/components/common/BadgeStatutOperationnel.vue'
import TauxCharge from '@/components/common/TauxCharge.vue'
import ReleveChargeForm from '@/components/charge/ReleveChargeForm.vue'
import InspectionForm from '@/components/inspections/InspectionForm.vue'
import InterventionForm from '@/components/interventions/InterventionForm.vue'
import TransformateurMap from '@/components/map/TransformateurMap.vue'
import PanneForm from '@/components/pannes/PanneForm.vue'
import HistoriqueTimeline from '@/components/transformateurs/HistoriqueTimeline.vue'
import TransformateurForm from '@/components/transformateurs/TransformateurForm.vue'
import { getErrorMessage } from '@/services/api'
import inspectionService from '@/services/inspectionService'
import interventionService from '@/services/interventionService'
import panneService from '@/services/panneService'
import releveChargeService from '@/services/releveChargeService'
import transformateurService from '@/services/transformateurService'
import { useAuthStore } from '@/stores/authStore'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { NIVEAU_HUILE_LABELS, formatDate, labelOf, todayISO } from '@/utils/format'
import { btnDanger, btnPrimary, btnSecondary, cardClass, inputClass } from '@/utils/ui'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const store = useTransformateurStore()

const id = computed(() => Number(route.params.id))
const data = ref(null) // { transformateur, total, evenements }
const loading = ref(false)
const error = ref('')
const ordre = ref('desc')

const t = computed(() => data.value?.transformateur ?? null)
const marqueurs = computed(() => (t.value ? [t.value] : []))

// Liste d'un seul poste pour les formulaires (puissance et tension BT servent à estimer le taux).
const listeTransformateur = computed(() =>
  t.value
    ? [
        {
          id: t.value.id,
          reference: t.value.reference,
          nom: t.value.nom,
          puissance: t.value.puissance,
          tension_bt: t.value.tension_bt,
        },
      ]
    : [],
)

const echeanceDepassee = computed(
  () => !!t.value?.prochaine_inspection && t.value.prochaine_inspection < todayISO(),
)

// Une fenêtre modale à la fois :
// 'transformateur' | 'inspection' | 'intervention' | 'releve' | 'panne' | null
const modal = ref(null)
const saving = ref(false)
const formError = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    data.value = await transformateurService.historique(id.value, ordre.value)
  } catch (e) {
    data.value = null
    error.value = getErrorMessage(e, 'Impossible de charger le transformateur')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  store.fetchSecteurs()
  load()
})
watch([id, ordre], load)

function ouvrir(nom) {
  formError.value = ''
  modal.value = nom
}

async function enregistrer(action) {
  saving.value = true
  formError.value = ''
  try {
    await action()
    modal.value = null
    await load()
  } catch (e) {
    formError.value = getErrorMessage(e, "Impossible d'enregistrer")
  } finally {
    saving.value = false
  }
}

const saveTransformateur = (payload) =>
  enregistrer(() => transformateurService.update(id.value, payload))
const saveInspection = (payload) =>
  enregistrer(() => inspectionService.create({ ...payload, transformateur_id: id.value }))
const saveIntervention = (payload) =>
  enregistrer(() => interventionService.create({ ...payload, transformateur_id: id.value }))
const saveReleve = (payload) =>
  enregistrer(() => releveChargeService.create({ ...payload, transformateur_id: id.value }))
const savePanne = (payload) =>
  enregistrer(() => panneService.create({ ...payload, transformateur_id: id.value }))

async function supprimer() {
  const ok = window.confirm(
    `Supprimer le transformateur ${t.value.reference} ?\nSes inspections, interventions, relevés et pannes seront aussi supprimés.`,
  )
  if (!ok) return
  try {
    await transformateurService.remove(id.value)
    router.push('/transformateurs')
  } catch (e) {
    error.value = getErrorMessage(e, 'Suppression impossible')
  }
}
</script>

<template>
  <div class="space-y-6">
    <RouterLink to="/transformateurs" class="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline">
      <ArrowLeft class="h-4 w-4" /> Retour à la liste
    </RouterLink>

    <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>
    <p v-else-if="loading && !t" class="text-sm text-slate-500">Chargement...</p>

    <template v-if="t">
      <!-- En-tête et actions -->
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div class="flex flex-wrap items-center gap-3">
            <h2 class="text-2xl font-bold text-slate-900">{{ t.reference }}</h2>
            <BadgeStatutOperationnel :statut="t.statut_operationnel" />
          </div>
          <p class="text-slate-600">{{ t.nom }} · {{ t.secteur }}</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <template v-if="auth.canWriteTerrain">
            <button type="button" :class="btnPrimary" @click="ouvrir('inspection')">
              <ClipboardCheck class="h-4 w-4" /> Inspection
            </button>
            <button type="button" :class="btnPrimary" @click="ouvrir('releve')">
              <Gauge class="h-4 w-4" /> Relevé de charge
            </button>
            <button type="button" :class="btnPrimary" @click="ouvrir('intervention')">
              <Wrench class="h-4 w-4" /> Intervention
            </button>
            <button type="button" :class="btnDanger" @click="ouvrir('panne')">
              <ShieldAlert class="h-4 w-4" /> Signaler une panne
            </button>
          </template>
          <template v-if="auth.canManageTransformateurs">
            <button type="button" :class="btnSecondary" @click="ouvrir('transformateur')">
              <Pencil class="h-4 w-4" /> Modifier
            </button>
            <button type="button" :class="btnDanger" @click="supprimer">
              <Trash2 class="h-4 w-4" /> Supprimer
            </button>
          </template>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Fiche technique -->
        <section :class="[cardClass, 'p-5']">
          <h3 class="mb-4 text-sm font-semibold text-slate-700">Fiche technique</h3>
          <dl class="space-y-3 text-sm">
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Quartier / secteur</dt>
              <dd class="font-medium">{{ t.secteur }}</dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Puissance nominale</dt>
              <dd class="font-medium">{{ t.puissance }} kVA</dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Tensions MT / BT</dt>
              <dd class="font-medium">{{ t.tension_mt }} kV / {{ t.tension_bt }} V</dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Huile diélectrique</dt>
              <dd class="text-right font-medium">{{ t.type_huile || '—' }}</dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Niveau d'huile</dt>
              <dd
                class="font-medium"
                :class="{ 'text-amber-700': t.niveau_huile === 'BAS', 'text-red-700': t.niveau_huile === 'CRITIQUE' }"
              >
                {{ labelOf(NIVEAU_HUILE_LABELS, t.niveau_huile) }}
              </dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Mise en service</dt>
              <dd class="font-medium">{{ formatDate(t.date_installation) }}</dd>
            </div>
            <div class="flex items-center justify-between gap-4">
              <dt class="text-slate-500">État technique</dt>
              <dd><BadgeEtat :etat="t.etat" /></dd>
            </div>
            <div class="flex items-center justify-between gap-4">
              <dt class="text-slate-500">Charge (dernier relevé)</dt>
              <dd><TauxCharge :taux="t.taux_charge" /></dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Pannes actives</dt>
              <dd class="font-medium" :class="t.nb_pannes_actives > 0 ? 'text-red-700' : ''">
                {{ t.nb_pannes_actives }}
              </dd>
            </div>
            <div class="flex items-center justify-between gap-4">
              <dt class="text-slate-500">Priorité préventive</dt>
              <dd><BadgePriorite :niveau="t.priorite" /></dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Dernière inspection</dt>
              <dd class="font-medium">{{ formatDate(t.derniere_inspection) }}</dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Prochaine inspection</dt>
              <dd class="text-right font-medium" :class="echeanceDepassee ? 'text-red-700' : ''">
                {{ formatDate(t.prochaine_inspection) }}
                <span v-if="echeanceDepassee" class="block text-xs font-normal">échéance dépassée</span>
                <span class="block text-xs font-normal text-slate-400">
                  périodicité : {{ t.periodicite_inspection_mois }} mois
                </span>
              </dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Activité</dt>
              <dd class="font-medium" :class="t.actif ? 'text-green-700' : 'text-slate-400'">
                {{ t.actif ? 'Actif' : 'Inactif' }}
              </dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-slate-500">Coordonnées</dt>
              <dd class="text-right font-mono text-xs">{{ t.latitude.toFixed(5) }}<br />{{ t.longitude.toFixed(5) }}</dd>
            </div>
          </dl>
        </section>

        <!-- Motifs de la priorité -->
        <section :class="[cardClass, 'p-5']">
          <h3 class="mb-4 text-sm font-semibold text-slate-700">Pourquoi cette priorité ?</h3>
          <ul class="list-inside list-disc space-y-1.5 text-sm text-slate-600">
            <li v-for="motif in t.priorite_motifs" :key="motif">{{ motif }}</li>
          </ul>
          <p class="mt-4 text-xs text-slate-400">
            Calcul automatique par règles simples : état, inspections, pannes, charge, niveau d'huile et échéance.
          </p>
        </section>

        <!-- Mini-carte -->
        <section :class="[cardClass, 'h-72 overflow-hidden p-1 lg:h-auto lg:min-h-[260px]']">
          <TransformateurMap :markers="marqueurs" :zoom="15" />
        </section>
      </div>

      <!-- Historique -->
      <section :class="[cardClass, 'p-5']">
        <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
          <h3 class="text-sm font-semibold text-slate-700">Historique ({{ data.total }} événement(s))</h3>
          <select v-model="ordre" :class="[inputClass, 'w-48']" aria-label="Ordre de tri">
            <option value="desc">Plus récent d'abord</option>
            <option value="asc">Plus ancien d'abord</option>
          </select>
        </div>
        <HistoriqueTimeline :evenements="data.evenements" />
      </section>

      <!-- Modales -->
      <AppModal :open="modal === 'transformateur'" :title="`Modifier ${t.reference}`" wide @close="modal = null">
        <TransformateurForm
          :transformateur="t"
          :secteurs="store.secteurs"
          :saving="saving"
          :error="formError"
          @submit="saveTransformateur"
          @cancel="modal = null"
        />
      </AppModal>

      <AppModal :open="modal === 'inspection'" :title="`Nouvelle inspection · ${t.reference}`" wide @close="modal = null">
        <InspectionForm
          :transformateurs="listeTransformateur"
          :locked-id="t.id"
          :saving="saving"
          :error="formError"
          @submit="saveInspection"
          @cancel="modal = null"
        />
      </AppModal>

      <AppModal :open="modal === 'intervention'" :title="`Nouvelle intervention · ${t.reference}`" wide @close="modal = null">
        <InterventionForm
          :transformateurs="listeTransformateur"
          :locked-id="t.id"
          :saving="saving"
          :error="formError"
          @submit="saveIntervention"
          @cancel="modal = null"
        />
      </AppModal>

      <AppModal :open="modal === 'releve'" :title="`Relevé de charge · ${t.reference}`" wide @close="modal = null">
        <ReleveChargeForm
          :transformateurs="listeTransformateur"
          :locked-id="t.id"
          :saving="saving"
          :error="formError"
          @submit="saveReleve"
          @cancel="modal = null"
        />
      </AppModal>

      <AppModal :open="modal === 'panne'" :title="`Signaler une panne · ${t.reference}`" wide @close="modal = null">
        <PanneForm
          :transformateurs="listeTransformateur"
          :locked-id="t.id"
          :saving="saving"
          :error="formError"
          @submit="savePanne"
          @cancel="modal = null"
        />
      </AppModal>
    </template>
  </div>
</template>