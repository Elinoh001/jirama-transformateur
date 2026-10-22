<script setup>
import { computed } from 'vue'

const props = defineProps({
  niveau: { type: String, default: null },
})

const STYLES = {
  NORMAL: { label: 'Normal', classes: 'bg-green-100 text-green-800' },
  A_SURVEILLER: { label: 'À surveiller', classes: 'bg-amber-100 text-amber-800' },
  PRIORITAIRE: { label: 'Prioritaire', classes: 'bg-red-100 text-red-800' },
}

const style = computed(
  () => STYLES[props.niveau] ?? { label: '—', classes: 'bg-slate-100 text-slate-600' },
)
</script>

<template>
  <span
    class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold"
    :class="style.classes"
  >
    {{ style.label }}
  </span>
</template>