<script setup>
import { computed } from 'vue'

import { formatPourcent } from '@/utils/format'

const props = defineProps({
  taux: { type: Number, default: null }, // taux de charge moyen fourni par l'API
})

// Demi-cercle de rayon 70 : longueur = pi x r
const LONGUEUR = Math.PI * 70

const decalage = computed(() => {
  const t = Math.min(Math.max(props.taux ?? 0, 0), 100)
  return LONGUEUR * (1 - t / 100)
})

const couleur = computed(() => {
  if (props.taux >= 120) return '#ef4444'
  if (props.taux > 100) return '#f97316'
  if (props.taux >= 80) return '#f59e0b'
  return '#22c55e'
})

const message = computed(() => {
  if (props.taux === null || props.taux === undefined) {
    return 'Aucun relevé de charge enregistré sur les postes actifs.'
  }
  if (props.taux > 100) return 'La charge moyenne dépasse la puissance nominale.'
  return 'La charge moyenne reste dans la capacité nominale.'
})
</script>

<template>
  <div class="flex flex-col items-center">
    <svg viewBox="0 0 180 105" class="w-full max-w-[260px]" role="img" aria-label="Taux de charge moyen">
      <path d="M 20 90 A 70 70 0 0 1 160 90" fill="none" stroke="#e2e8f0" stroke-width="14" stroke-linecap="round" />
      <path
        v-if="taux !== null && taux !== undefined"
        d="M 20 90 A 70 70 0 0 1 160 90"
        fill="none"
        :stroke="couleur"
        stroke-width="14"
        stroke-linecap="round"
        :stroke-dasharray="LONGUEUR"
        :stroke-dashoffset="decalage"
      />
      <text x="90" y="78" text-anchor="middle" class="fill-navy-900 text-2xl font-bold">
        {{ formatPourcent(taux) }}
      </text>
      <text x="90" y="95" text-anchor="middle" class="fill-slate-500 text-[10px]">Moyenne des derniers relevés</text>
    </svg>
    <p class="mt-2 text-center text-xs text-slate-500">{{ message }}</p>
  </div>
</template>