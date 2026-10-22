<script setup>
import { computed } from 'vue'

import { formatPourcent } from '@/utils/format'

const props = defineProps({
  taux: { type: Number, default: null },
})

const largeur = computed(() => Math.min(Math.max(props.taux ?? 0, 0), 100))

// Vert jusqu'à 80 %, jaune de 80 à 100 %, orange en surcharge, rouge à partir de 120 %.
const couleur = computed(() => {
  if (props.taux >= 120) return 'bg-red-500'
  if (props.taux > 100) return 'bg-orange-500'
  if (props.taux >= 80) return 'bg-amber-400'
  return 'bg-green-500'
})
</script>

<template>
  <span v-if="taux === null || taux === undefined" class="text-slate-400">—</span>
  <div v-else class="min-w-[90px]">
    <span class="text-sm font-medium" :class="taux > 100 ? 'text-orange-700' : 'text-slate-800'">
      {{ formatPourcent(taux) }}
    </span>
    <div class="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
      <div class="h-full rounded-full" :class="couleur" :style="{ width: largeur + '%' }"></div>
    </div>
  </div>
</template>