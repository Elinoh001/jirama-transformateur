<script setup>
import { computed } from 'vue'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  activite: { type: Array, required: true }, // [{ mois, inspections, interventions }]
})

const data = computed(() => ({
  labels: props.activite.map((a) => a.mois),
  datasets: [
    {
      label: 'Inspections',
      data: props.activite.map((a) => a.inspections),
      backgroundColor: '#3b82f6',
      borderRadius: 4,
    },
    {
      label: 'Interventions',
      data: props.activite.map((a) => a.interventions),
      backgroundColor: '#f59e0b',
      borderRadius: 4,
    },
  ],
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
  scales: {
    y: { beginAtZero: true, ticks: { precision: 0 } },
  },
}
</script>

<template>
  <div class="h-64">
    <Bar :data="data" :options="options" />
  </div>
</template>