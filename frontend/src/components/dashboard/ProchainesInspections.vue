<script setup>
import { CalendarClock } from 'lucide-vue-next'

import BadgePriorite from '@/components/common/BadgePriorite.vue'
import { formatDate } from '@/utils/format'

defineProps({
  data: { type: Object, default: null }, // { en_retard, items }
  loading: { type: Boolean, default: false },
})

function libelleJours(jours) {
  if (jours < 0) return `en retard de ${-jours} j`
  if (jours === 0) return "aujourd'hui"
  return `dans ${jours} j`
}

function classeJours(jours) {
  if (jours < 0) return 'text-red-600'
  if (jours <= 30) return 'text-amber-600'
  return 'text-slate-500'
}
</script>

<template>
  <p v-if="!data && loading" class="py-6 text-center text-sm text-slate-500">Chargement...</p>
  <p v-else-if="!data" class="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
    Échéances indisponibles : vérifiez que le backend est à jour (endpoint inspections-a-venir).
  </p>

  <div v-else>
    <p v-if="data.en_retard > 0" class="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm font-medium text-red-700">
      {{ data.en_retard }} poste(s) actif(s) avec une inspection en retard.
    </p>

    <p v-if="data.items.length === 0" class="py-6 text-center text-sm text-slate-500">
      Aucune échéance d'inspection enregistrée.
    </p>

    <ul v-else class="divide-y divide-slate-100">
      <li v-for="i in data.items" :key="i.transformateur_id">
        <RouterLink
          :to="`/transformateurs/${i.transformateur_id}`"
          class="flex items-center gap-3 py-3 hover:bg-slate-50"
        >
          <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
            <CalendarClock class="h-5 w-5" />
          </span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-sm font-semibold text-navy-900">{{ i.reference }} · {{ i.nom }}</span>
            <span class="block text-xs text-slate-500">{{ formatDate(i.prochaine_inspection) }} · {{ i.secteur }}</span>
          </span>
          <span class="flex flex-col items-end gap-1">
            <BadgePriorite :niveau="i.niveau" />
            <span class="text-xs font-semibold" :class="classeJours(i.jours_restants)">
              {{ libelleJours(i.jours_restants) }}
            </span>
          </span>
        </RouterLink>
      </li>
    </ul>

    <p class="mt-3 rounded-lg bg-blue-50 px-3 py-2 text-xs text-blue-800">
      Échéance = dernière inspection réalisée + périodicité du poste. Les inspections programmées se consultent
      dans la page Inspections.
    </p>
  </div>
</template>