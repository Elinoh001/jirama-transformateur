<script setup>
import { computed } from 'vue'
import { ArcElement, Chart as ChartJS, Tooltip } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

import { formatPourcent } from '@/utils/format'

ChartJS.register(ArcElement, Tooltip)

const props = defineProps({
  bon: { type: Number, default: 0 },
  surveiller: { type: Number, default: 0 },
  critique: { type: Number, default: 0 },
})

const total = computed(() => props.bon + props.surveiller + props.critique)

const lignes = computed(() => [
  { label: 'Bon état', n: props.bon, couleur: '#22c55e' },
  { label: 'À surveiller', n: props.surveiller, couleur: '#f59e0b' },
  { label: 'Critique', n: props.critique, couleur: '#ef4444' },
])

const data = computed(() => ({
  labels: lignes.value.map((l) => l.label),
  datasets: [
    {
      data: lignes.value.map((l) => l.n),
      backgroundColor: lignes.value.map((l) => l.couleur),
      borderWidth: 2,
      borderColor: '#ffffff',
    },
  ],
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  plugins: { legend: { display: false } },
}

function pourcent(n) {
  return total.value ? formatPourcent((n / total.value) * 100) : '—'
}
</script>

<template>
  <div class="flex flex-wrap items-center justify-center gap-6">
    <div class="relative h-44 w-44 shrink-0">
      <Doughnut :data="data" :options="options" />
      <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span class="text-3xl font-bold text-navy-900">{{ total }}</span>
        <span class="text-xs text-slate-500">Total</span>
      </div>
    </div>

    <ul class="space-y-3 text-sm">
      <li v-for="l in lignes" :key="l.label" class="flex items-center gap-3">
        <span class="h-3 w-3 shrink-0 rounded-full" :style="{ background: l.couleur }"></span>
        <span class="w-24 text-slate-700">{{ l.label }}</span>
        <span class="font-semibold text-navy-900">{{ l.n }}</span>
        <span class="text-slate-500">({{ pourcent(l.n) }})</span>
      </li>
    </ul>
  </div>
</template>