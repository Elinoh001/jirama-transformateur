<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import TransformateurMap from '@/components/map/TransformateurMap.vue'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { COULEURS_PRIORITE, COULEURS_STATUT } from '@/utils/couleurs'
import { PRIORITE_LABELS, STATUT_OPERATIONNEL_LABELS } from '@/utils/format'
import { cardClass, inputClass } from '@/utils/ui'

const router = useRouter()
const store = useTransformateurStore()

const colorBy = ref('statut')
const secteur = ref('')
const statut = ref('')
const niveau = ref('')
const afficherInactifs = ref(false)

const markers = computed(() =>
  store.items.filter((t) => {
    if (!afficherInactifs.value && !t.actif) return false
    if (secteur.value && t.secteur !== secteur.value) return false
    if (statut.value && t.statut_operationnel !== statut.value) return false
    if (niveau.value && t.priorite !== niveau.value) return false
    return true
  }),
)

const legende = computed(() => {
  const source = colorBy.value === 'statut' ? COULEURS_STATUT : COULEURS_PRIORITE
  const labels = colorBy.value === 'statut' ? STATUT_OPERATIONNEL_LABELS : PRIORITE_LABELS
  return Object.entries(source).map(([cle, couleur]) => ({ label: labels[cle], couleur }))
})

onMounted(() => {
  store.fetchAll()
  store.fetchSecteurs()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4">
    <div :class="[cardClass, 'flex flex-wrap items-end gap-4 p-4']">
      <div>
        <label for="m-couleur" class="mb-1 block text-xs font-medium text-slate-500">Couleur selon</label>
        <select id="m-couleur" v-model="colorBy" :class="[inputClass, 'w-48']">
          <option value="statut">Statut opérationnel</option>
          <option value="priorite">Priorité préventive</option>
        </select>
      </div>
      <div>
        <label for="m-secteur" class="mb-1 block text-xs font-medium text-slate-500">Quartier / secteur</label>
        <select id="m-secteur" v-model="secteur" :class="[inputClass, 'w-48']">
          <option value="">Tous</option>
          <option v-for="s in store.secteurs" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div>
        <label for="m-statut" class="mb-1 block text-xs font-medium text-slate-500">Statut</label>
        <select id="m-statut" v-model="statut" :class="[inputClass, 'w-44']">
          <option value="">Tous</option>
          <option v-for="(label, value) in STATUT_OPERATIONNEL_LABELS" :key="value" :value="value">
            {{ label }}
          </option>
        </select>
      </div>
      <div>
        <label for="m-niveau" class="mb-1 block text-xs font-medium text-slate-500">Priorité</label>
        <select id="m-niveau" v-model="niveau" :class="[inputClass, 'w-40']">
          <option value="">Toutes</option>
          <option v-for="(label, value) in PRIORITE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>

      <label class="mb-2 flex cursor-pointer items-center gap-2 text-sm text-slate-700">
        <input v-model="afficherInactifs" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
        Afficher les inactifs
      </label>

      <div class="mb-2 ml-auto flex flex-wrap items-center gap-4 text-sm text-slate-600">
        <span v-for="l in legende" :key="l.label" class="flex items-center gap-1.5">
          <span class="inline-block h-3 w-3 rounded-full" :style="{ background: l.couleur }"></span>
          {{ l.label }}
        </span>
        <span class="font-medium text-slate-800">{{ markers.length }} affiché(s)</span>
      </div>
    </div>

    <p v-if="store.error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ store.error }}</p>

    <div :class="[cardClass, 'min-h-[420px] flex-1 overflow-hidden p-1']">
      <TransformateurMap
        :markers="markers"
        :color-by="colorBy"
        @open="(id) => router.push(`/transformateurs/${id}`)"
      />
    </div>
  </div>
</template>