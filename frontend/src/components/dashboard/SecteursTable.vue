<script setup>
import { thClass } from '@/utils/ui'

defineProps({
  secteurs: { type: Array, required: true }, // [{ secteur, total, en_surcharge, en_panne, pannes_actives }]
})
</script>

<template>
  <p v-if="secteurs.length === 0" class="py-6 text-center text-sm text-slate-500">Aucun poste actif.</p>

  <div v-else class="overflow-x-auto">
    <table class="min-w-full text-sm">
      <thead class="border-b border-slate-200">
        <tr>
          <th :class="thClass">Secteur</th>
          <th :class="[thClass, 'text-right']">Postes</th>
          <th :class="[thClass, 'text-right']">En surcharge</th>
          <th :class="[thClass, 'text-right']">En panne</th>
          <th :class="[thClass, 'text-right']">Pannes actives</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="s in secteurs" :key="s.secteur" class="hover:bg-slate-50">
          <td class="px-3 py-2 font-medium">{{ s.secteur }}</td>
          <td class="px-3 py-2 text-right">{{ s.total }}</td>
          <td class="px-3 py-2 text-right" :class="s.en_surcharge > 0 ? 'font-semibold text-orange-700' : 'text-slate-400'">
            {{ s.en_surcharge }}
          </td>
          <td class="px-3 py-2 text-right" :class="s.en_panne > 0 ? 'font-semibold text-red-700' : 'text-slate-400'">
            {{ s.en_panne }}
          </td>
          <td class="px-3 py-2 text-right" :class="s.pannes_actives > 0 ? 'font-semibold text-red-700' : 'text-slate-400'">
            {{ s.pannes_actives }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>