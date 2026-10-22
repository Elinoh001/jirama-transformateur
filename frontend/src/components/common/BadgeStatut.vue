<script setup>
import { computed } from 'vue'

import { STATUT_LABELS } from '@/utils/format'

const props = defineProps({
  statut: { type: String, required: true },
})

const CLASSES = {
  PLANIFIEE: 'bg-blue-100 text-blue-800',
  EN_COURS: 'bg-amber-100 text-amber-800',
  TERMINEE: 'bg-green-100 text-green-800',
  ANNULEE: 'bg-slate-200 text-slate-600',
}

const classes = computed(() => CLASSES[props.statut] ?? 'bg-slate-100 text-slate-700')
</script>

<template>
  <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="classes">
    {{ STATUT_LABELS[statut] ?? statut }}
  </span>
</template>