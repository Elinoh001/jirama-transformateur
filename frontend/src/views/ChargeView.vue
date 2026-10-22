<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { Plus } from 'lucide-vue-next'

import AppModal from '@/components/common/AppModal.vue'
import BadgeTag from '@/components/common/BadgeTag.vue'
import TauxCharge from '@/components/common/TauxCharge.vue'
import ReleveChargeForm from '@/components/charge/ReleveChargeForm.vue'
import { getErrorMessage } from '@/services/api'
import releveChargeService from '@/services/releveChargeService'
import { useAuthStore } from '@/stores/authStore'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { formatDate } from '@/utils/format'
import { btnPrimary, cardClass, inputClass, thClass } from '@/utils/ui'

const auth = useAuthStore()
const transformateurs = useTransformateurStore()

const releves = ref([])
const loading = ref(false)
const error = ref('')

const filtreTransformateur = ref('')
const filtreSurcharge = ref('')

const showForm = ref(false)
const saving = ref(false)
const formError = ref('')

const nbSurcharges = computed(() => releves.value.filter((r) => r.surcharge).length)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filtreTransformateur.value) params.transformateur_id = filtreTransformateur.value
    if (filtreSurcharge.value !== '') params.surcharge = filtreSurcharge.value === 'true'
    releves.value = await releveChargeService.list(params)
  } catch (e) {
    error.value = getErrorMessage(e, 'Impossible de charger les relevés')
  } finally {
    loading.value = false
  }
}

watch([filtreTransformateur, filtreSurcharge], load)
onMounted(() => {
  transformateurs.fetchAll()
  load()
})

function ouvrirCreation() {
  formError.value = ''
  showForm.value = true
}

async function enregistrer(payload) {
  saving.value = true
  formError.value = ''
  try {
    await releveChargeService.create(payload)
    showForm.value = false
    await load()
    await transformateurs.fetchAll() // le statut des postes a pu changer
  } catch (e) {
    formError.value = getErrorMessage(e, "Impossible d'enregistrer le relevé")
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
        <label for="f-surcharge" class="mb-1 block text-xs font-medium text-slate-500">Charge</label>
        <select id="f-surcharge" v-model="filtreSurcharge" :class="[inputClass, 'w-44']">
          <option value="">Tous les relevés</option>
          <option value="true">En surcharge (&gt; 100 %)</option>
          <option value="false">Normale (≤ 100 %)</option>
        </select>
      </div>
      <button v-if="auth.canWriteTerrain" type="button" :class="[btnPrimary, 'ml-auto']" @click="ouvrirCreation">
        <Plus class="h-4 w-4" /> Nouveau relevé
      </button>
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>

    <div :class="[cardClass, 'overflow-x-auto']">
      <table class="min-w-full text-sm">
        <thead class="border-b border-slate-200 bg-slate-50">
          <tr>
            <th :class="thClass">Date</th>
            <th :class="thClass">Transformateur</th>
            <th :class="thClass">Mesurée</th>
            <th :class="thClass">Courant</th>
            <th :class="thClass">Nominale</th>
            <th :class="thClass">Taux de charge</th>
            <th :class="thClass">Alerte</th>
            <th :class="thClass">Relevé par</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="loading && releves.length === 0">
            <td colspan="8" class="px-3 py-8 text-center text-slate-500">Chargement...</td>
          </tr>
          <tr v-else-if="releves.length === 0">
            <td colspan="8" class="px-3 py-8 text-center text-slate-500">Aucun relevé trouvé.</td>
          </tr>
          <tr v-for="r in releves" :key="r.id" class="hover:bg-slate-50">
            <td class="whitespace-nowrap px-3 py-3">{{ formatDate(r.date_releve) }}</td>
            <td class="px-3 py-3">
              <RouterLink :to="`/transformateurs/${r.transformateur_id}`" class="font-medium text-blue-600 hover:underline">
                {{ r.transformateur_reference }}
              </RouterLink>
              <span class="block text-xs text-slate-500">{{ r.transformateur_nom }}</span>
            </td>
            <td class="whitespace-nowrap px-3 py-3">{{ r.puissance_mesuree }} kVA</td>
            <td class="whitespace-nowrap px-3 py-3 text-slate-600">
              {{ r.courant_mesure !== null ? r.courant_mesure + ' A' : '—' }}
            </td>
            <td class="whitespace-nowrap px-3 py-3 text-slate-600">{{ r.puissance_nominale }} kVA</td>
            <td class="px-3 py-3"><TauxCharge :taux="r.taux_charge" /></td>
            <td class="px-3 py-3">
              <BadgeTag v-if="r.surcharge" label="Surcharge" tone="orange" />
              <BadgeTag v-else label="Normale" tone="green" />
            </td>
            <td class="whitespace-nowrap px-3 py-3">{{ r.releve_par }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="text-xs text-slate-500">{{ releves.length }} relevé(s), dont {{ nbSurcharges }} en surcharge</p>

    <AppModal :open="showForm" title="Nouveau relevé de charge" wide @close="showForm = false">
      <ReleveChargeForm
        :transformateurs="transformateurs.items"
        :saving="saving"
        :error="formError"
        @submit="enregistrer"
        @cancel="showForm = false"
      />
    </AppModal>
  </div>
</template>