<script setup>
import { computed } from 'vue'

import BadgeTag from '@/components/common/BadgeTag.vue'
import { STATUT_OPERATIONNEL_LABELS, labelOf } from '@/utils/format'

const props = defineProps({
  statut: { type: String, default: null },
})

const TONES = {
  EN_SERVICE: 'green',
  EN_SURCHARGE: 'orange',
  EN_MAINTENANCE: 'blue',
  EN_PANNE: 'red',
}

const label = computed(() => (props.statut ? labelOf(STATUT_OPERATIONNEL_LABELS, props.statut) : '—'))
const tone = computed(() => TONES[props.statut] ?? 'slate')
</script>

<template>
  <BadgeTag :label="label" :tone="tone" />
</template>