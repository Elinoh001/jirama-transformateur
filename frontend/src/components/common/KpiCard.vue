<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  subtitle: { type: String, default: '' },
  icon: { type: [Object, Function], default: null },
  tone: { type: String, default: 'blue' }, // blue | green | amber | red
  to: { type: String, default: '' }, // lien facultatif vers la liste correspondante
})

const ICONES = {
  blue: 'bg-blue-600',
  green: 'bg-green-500',
  amber: 'bg-amber-400',
  red: 'bg-red-500',
}
const SOUS_TITRES = {
  blue: 'text-blue-600',
  green: 'text-green-600',
  amber: 'text-amber-600',
  red: 'text-red-600',
}

const iconeClasses = computed(() => ICONES[props.tone] ?? ICONES.blue)
const sousTitreClasses = computed(() => SOUS_TITRES[props.tone] ?? SOUS_TITRES.blue)
</script>

<template>
  <component
    :is="to ? 'RouterLink' : 'div'"
    :to="to || undefined"
    class="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
    :class="to ? 'transition-shadow hover:shadow-md' : ''"
  >
    <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full text-white" :class="iconeClasses">
      <component :is="icon" v-if="icon" class="h-7 w-7" />
    </div>
    <div class="min-w-0">
      <p class="truncate text-sm font-medium text-slate-600">{{ label }}</p>
      <p class="text-3xl font-bold leading-tight text-navy-900">{{ value }}</p>
      <p v-if="subtitle" class="truncate text-xs font-semibold" :class="sousTitreClasses">{{ subtitle }}</p>
    </div>
  </component>
</template>