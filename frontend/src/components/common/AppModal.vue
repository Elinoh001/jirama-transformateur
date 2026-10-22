<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import { X } from 'lucide-vue-next'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  wide: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])

function onKeydown(event) {
  if (event.key === 'Escape') emit('close')
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[1000] flex items-start justify-center overflow-y-auto bg-slate-900/50 p-4 sm:items-center"
      @mousedown.self="emit('close')"
    >
      <div
        class="w-full rounded-2xl bg-white shadow-xl"
        :class="wide ? 'max-w-2xl' : 'max-w-lg'"
        role="dialog"
        aria-modal="true"
      >
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-3">
          <h2 class="text-base font-semibold text-slate-800">{{ title }}</h2>
          <button
            type="button"
            class="cursor-pointer rounded-md p-1 text-slate-500 hover:bg-slate-100"
            aria-label="Fermer"
            @click="emit('close')"
          >
            <X class="h-5 w-5" />
          </button>
        </div>
        <div class="p-5">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>