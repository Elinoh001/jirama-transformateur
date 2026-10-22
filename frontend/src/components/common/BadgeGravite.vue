<script setup>
import { computed } from 'vue'

import BadgeTag from '@/components/common/BadgeTag.vue'
import { GRAVITE_LABELS, labelOf } from '@/utils/format'

const props = defineProps({
  gravite: { type: String, default: null },
})

const TONES = { MINEURE: 'slate', MAJEURE: 'amber', CRITIQUE: 'red' }

const label = computed(() => (props.gravite ? labelOf(GRAVITE_LABELS, props.gravite) : '—'))
const tone = computed(() => TONES[props.gravite] ?? 'slate')
</script>

<template>
  <BadgeTag :label="label" :tone="tone" />
</template>