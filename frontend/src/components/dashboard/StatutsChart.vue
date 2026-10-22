<script setup>
import { computed } from 'vue'
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

import { COULEURS_STATUT } from '@/utils/couleurs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  repartition: { type: Object, required: true }, // { en_service, en_surcharge, en_maintenance, en_panne }
})

const data = computed(() => ({
  labels: ['En service', 'En surcharge', 'En maintenance', 'En panne'],
  datasets: [
    {
      data: [
        props.repartition.en_service,
        props.repartition.en_surcharge,
        props.repartition.en_maintenance,
        props.repartition.en_panne,
      ],
      backgroundColor: [
        COULEURS_STATUT.EN_SERVICE,
        COULEURS_STATUT.EN_SURCHARGE,
        COULEURS_STATUT.EN_MAINTENANCE,
        COULEURS_STATUT.EN_PANNE,
      ],
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