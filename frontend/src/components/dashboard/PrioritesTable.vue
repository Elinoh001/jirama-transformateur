<script setup>
import BadgePriorite from '@/components/common/BadgePriorite.vue'
import BadgeStatutOperationnel from '@/components/common/BadgeStatutOperationnel.vue'
import { formatDate } from '@/utils/format'

defineProps({
  items: { type: Array, required: true },
})
</script>

<template>
  <div v-if="items.length === 0" class="py-8 text-center text-sm text-slate-500">
    Aucun transformateur à traiter en priorité.
  </div>

  <div v-else class="overflow-x-auto">
    <table class="min-w-full text-sm">
      <thead>
        <tr class="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-500">
          <th class="px-3 py-2 font-semibold">Référence</th>
          <th class="px-3 py-2 font-semibold">Nom</th>
          <th class="px-3 py-2 font-semibold">Secteur</th>
          <th class="px-3 py-2 font-semibold">Statut</th>
          <th class="px-3 py-2 font-semibold">Priorité</th>
          <th class="px-3 py-2 font-semibold">Motifs</th>
          <th class="px-3 py-2 font-semibold">Dernière inspection</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="item in items" :key="item.transformateur_id" class="align-top hover:bg-slate-50">
          <td class="whitespace-nowrap px-3 py-3 font-medium">
            <RouterLink
              :to="`/transformateurs/${item.transformateur_id}`"
              class="text-blue-600 hover:underline"
            >
              {{ item.reference }}
            </RouterLink>
          </td>
          <td class="px-3 py-3">{{ item.nom }}</td>
          <td class="whitespace-nowrap px-3 py-3 text-slate-600">{{ item.secteur }}</td>
          <td class="px-3 py-3"><BadgeStatutOperationnel :statut="item.statut_operationnel" /></td>
          <td class="px-3 py-3"><BadgePriorite :niveau="item.niveau" /></td>
          <td class="px-3 py-3 text-slate-600">
            <ul class="list-inside list-disc space-y-0.5">
              <li v-for="motif in item.motifs" :key="motif">{{ motif }}</li>
            </ul>
          </td>
          <td class="whitespace-nowrap px-3 py-3 text-slate-600">
            {{ formatDate(item.derniere_inspection) }}
            <span v-if="item.jours_depuis_derniere_inspection !== null" class="block text-xs text-slate-400">
              il y a {{ item.jours_depuis_derniere_inspection }} j
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>