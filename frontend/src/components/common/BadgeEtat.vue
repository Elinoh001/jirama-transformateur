<script setup>
import { computed } from 'vue'

const props = defineProps({
  etat: { type: String, required: true },
})

const STYLES = {
  BON: { label: 'Bon', classes: 'bg-green-100 text-green-800' },
  A_SURVEILLER: { label: 'À surveiller', classes: 'bg-amber-100 text-amber-800' },
  CRITIQUE: { label: 'Critique', classes: 'bg-red-100 text-red-800' },
}

const style = computed(
  () => STYLES[props.etat] ?? { label: props.etat, classes: 'bg-slate-100 text-slate-700' },
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