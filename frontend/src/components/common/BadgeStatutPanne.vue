<script setup>
import { computed } from 'vue'

import BadgeTag from '@/components/common/BadgeTag.vue'
import { STATUT_PANNE_LABELS, labelOf } from '@/utils/format'

const props = defineProps({
  statut: { type: String, default: null },
})

const TONES = { SIGNALEE: 'red', EN_COURS: 'amber', RESOLUE: 'green' }

const label = computed(() => (props.statut ? labelOf(STATUT_PANNE_LABELS, props.statut) : '—'))
const tone = computed(() => TONES[props.statut] ?? 'slate')
</script>

<template>
  <BadgeTag :label="label" :tone="tone" />
</template>