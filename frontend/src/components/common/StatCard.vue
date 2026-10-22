<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  icon: { type: [Object, Function], default: null },
  tone: { type: String, default: 'slate' }, // slate | blue | green | amber | red
})

const TONES = {
  slate: 'bg-slate-100 text-slate-600',
  blue: 'bg-blue-100 text-blue-600',
  green: 'bg-green-100 text-green-600',
  amber: 'bg-amber-100 text-amber-600',
  red: 'bg-red-100 text-red-600',
}

const toneClasses = computed(() => TONES[props.tone] ?? TONES.slate)
</script>

<template>
  <div class="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
    <div v-if="icon" class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg" :class="toneClasses">
      <component :is="icon" class="h-6 w-6" />
    </div>
    <div class="min-w-0">
      <p class="text-2xl font-bold text-slate-900">{{ value }}</p>
      <p class="truncate text-sm text-slate-500">{{ label }}</p>
    </div>
  </div>
</template>