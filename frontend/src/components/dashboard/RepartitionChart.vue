<script setup>
import { computed } from 'vue'
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  repartition: { type: Object, required: true }, // { normal, a_surveiller, prioritaire }
})

const data = computed(() => ({
  labels: ['Normal', 'À surveiller', 'Prioritaire'],
  datasets: [
    {
      data: [
        props.repartition.normal,
        props.repartition.a_surveiller,
        props.repartition.prioritaire,
      ],
      backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
      borderWidth: 2,
      borderColor: '#ffffff',
    },
  ],
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '62%',
  plugins: { legend: { position: 'bottom' } },
}
</script>

<template>
  <div class="h-64">
    <Doughnut :data="data" :options="options" />
  </div>
</template>