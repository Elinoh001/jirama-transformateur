<script setup>
import { ClipboardCheck, ShieldAlert, Wrench } from 'lucide-vue-next'

import BadgeEtat from '@/components/common/BadgeEtat.vue'
import BadgeGravite from '@/components/common/BadgeGravite.vue'
import BadgeStatut from '@/components/common/BadgeStatut.vue'
import BadgeStatutInspection from '@/components/common/BadgeStatutInspection.vue'
import BadgeStatutPanne from '@/components/common/BadgeStatutPanne.vue'
import {
  TYPE_INSPECTION_LABELS,
  TYPE_INTERVENTION_LABELS,
  TYPE_PANNE_LABELS,
  formatDate,
  formatMontant,
  labelOf,
} from '@/utils/format'

defineProps({
  evenements: { type: Array, required: true },
})

const TITRES = { INSPECTION: 'Inspection', INTERVENTION: 'Intervention', PANNE: 'Panne' }
const COULEURS = {
  INSPECTION: 'bg-blue-600 text-white',
  INTERVENTION: 'bg-amber-500 text-white',
  PANNE: 'bg-red-600 text-white',
}

function typeLabel(e) {
  if (e.evenement === 'INSPECTION') return labelOf(TYPE_INSPECTION_LABELS, e.type)
  if (e.evenement === 'INTERVENTION') return labelOf(TYPE_INTERVENTION_LABELS, e.type)
  return labelOf(TYPE_PANNE_LABELS, e.type)
}
</script>

<template>
  <p v-if="evenements.length === 0" class="py-6 text-center text-sm text-slate-500">
    Aucun événement enregistré pour ce transformateur.
  </p>

  <ol v-else class="relative ml-3 space-y-5 border-l-2 border-slate-200 pl-6">
    <li v-for="e in evenements" :key="`${e.evenement}-${e.id}`" class="relative">
      <span
        class="absolute -left-[37px] flex h-7 w-7 items-center justify-center rounded-full ring-4 ring-white"
        :class="COULEURS[e.evenement]"
      >
        <ClipboardCheck v-if="e.evenement === 'INSPECTION'" class="h-4 w-4" />
        <Wrench v-else-if="e.evenement === 'INTERVENTION'" class="h-4 w-4" />
        <ShieldAlert v-else class="h-4 w-4" />
      </span>

      <div class="flex flex-wrap items-center gap-2">
        <span class="text-sm font-semibold text-slate-800">{{ formatDate(e.date_evenement) }}</span>
        <span class="text-sm text-slate-600">{{ TITRES[e.evenement] }} · {{ typeLabel(e) }}</span>

        <template v-if="e.evenement === 'INSPECTION'">
          <BadgeStatutInspection :statut="e.statut" />
          <BadgeEtat v-if="e.etat" :etat="e.etat" />
        </template>
        <BadgeStatut v-else-if="e.evenement === 'INTERVENTION'" :statut="e.statut" />
        <template v-else>
          <BadgeGravite :gravite="e.gravite" />
          <BadgeStatutPanne :statut="e.statut" />
        </template>
      </div>

      <p v-if="e.resume" class="mt-1 text-sm text-slate-600">{{ e.resume }}</p>
      <p class="mt-1 text-xs text-slate-400">
        {{ e.evenement === 'PANNE' ? 'Signalée par' : 'Technicien' }} : {{ e.technicien }}
        <template v-if="e.cout !== null && e.cout !== undefined"> · Coût : {{ formatMontant(e.cout) }}</template>
      </p>
    </li>
  </ol>
</template>