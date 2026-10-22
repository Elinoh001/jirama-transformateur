<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, default: '—' },
  tone: { type: String, default: 'slate' }, // slate | gray | blue | green | amber | orange | red
})

const TONES = {
  slate: 'bg-slate-100 text-slate-700',
  gray: 'bg-slate-200 text-slate-600',
  blue: 'bg-blue-100 text-blue-800',
  green: 'bg-green-100 text-green-800',
  amber: 'bg-amber-100 text-amber-800',
  orange: 'bg-orange-100 text-orange-800',
  red: 'bg-red-100 text-red-800',
}

const classes = computed(() => TONES[props.tone] ?? TONES.slate)
</script>

<template>
  <span class="inline-flex items-center whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="classes">
    {{ label }}
  </span>
</template>