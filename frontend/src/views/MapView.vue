<script setup>
import { computed, onMounted, ref } from 'vue'
import { Search } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import TransformateurMap from '@/components/map/TransformateurMap.vue'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { PRIORITE_LABELS, STATUT_OPERATIONNEL_LABELS } from '@/utils/format'
import { cardClass, inputClass } from '@/utils/ui'

const router = useRouter()
const store = useTransformateurStore()

const colorBy = ref('statut')
const recherche = ref('')
const secteur = ref('')
const statut = ref('')
const niveau = ref('')
const afficherInactifs = ref(false)

const markers = computed(() => {
  const q = recherche.value.trim().toLowerCase()
  return store.items.filter((t) => {
    if (!afficherInactifs.value && !t.actif) return false
    if (secteur.value && t.secteur !== secteur.value) return false
    if (statut.value && t.statut_operationnel !== statut.value) return false
    if (niveau.value && t.priorite !== niveau.value) return false
    if (q && ![t.reference, t.nom, t.secteur].some((v) => v?.toLowerCase().includes(q))) return false
    return true
  })
})

onMounted(() => {
  store.fetchAll()
  store.fetchSecteurs()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4">
    <div :class="[cardClass, 'flex flex-wrap items-end gap-4 p-4']">
      <div class="min-w-[200px] flex-1">
        <label for="m-recherche" class="mb-1 block text-xs font-medium text-slate-500">Recherche</label>
        <div class="relative">
          <Search class="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            id="m-recherche"
            v-model="recherche"
            placeholder="Référence, nom ou quartier"
            :class="[inputClass, 'pl-9']"
          />
        </div>
      </div>
      <div>
        <label for="m-couleur" class="mb-1 block text-xs font-medium text-slate-500">Couleur selon</label>
        <select id="m-couleur" v-model="colorBy" :class="[inputClass, 'w-48']">
          <option value="statut">Statut opérationnel</option>
          <option value="priorite">Priorité préventive</option>
        </select>
      </div>
      <div>
        <label for="m-secteur" class="mb-1 block text-xs font-medium text-slate-500">Quartier / secteur</label>
        <select id="m-secteur" v-model="secteur" :class="[inputClass, 'w-44']">
          <option value="">Tous</option>
          <option v-for="s in store.secteurs" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div>
        <label for="m-statut" class="mb-1 block text-xs font-medium text-slate-500">Statut</label>
        <select id="m-statut" v-model="statut" :class="[inputClass, 'w-44']">
          <option value="">Tous</option>
          <option v-for="(label, value) in STATUT_OPERATIONNEL_LABELS" :key="value" :value="value">
            {{ label }}
          </option>
        </select>
      </div>
      <div>
        <label for="m-niveau" class="mb-1 block text-xs font-medium text-slate-500">Priorité</label>
        <select id="m-niveau" v-model="niveau" :class="[inputClass, 'w-40']">
          <option value="">Toutes</option>
          <option v-for="(label, value) in PRIORITE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>

      <label class="mb-2 flex cursor-pointer items-center gap-2 text-sm text-slate-700">
        <input v-model="afficherInactifs" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
        Afficher les inactifs
      </label>

      <span class="mb-2 ml-auto text-sm font-medium text-navy-900">{{ markers.length }} affiché(s)</span>
    </div>

    <p v-if="store.error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ store.error }}</p>

    <div :class="[cardClass, 'min-h-[420px] flex-1 overflow-hidden p-1']">
      <TransformateurMap
        :markers="markers"
        :color-by="colorBy"
        @open="(id) => router.push(`/transformateurs/${id}`)"
      />
    </div>
  </div>
</template>