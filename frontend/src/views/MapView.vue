<script setup>
import { computed, onMounted, ref } from 'vue'
import { Search, SlidersHorizontal, MapPin } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import TransformateurMap from '@/components/map/TransformateurMap.vue'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { PRIORITE_LABELS, STATUT_OPERATIONNEL_LABELS } from '@/utils/format'

const router = useRouter()
const store = useTransformateurStore()

const colorBy = ref('statut')
const recherche = ref('')
const secteur = ref('')
const statut = ref('')
const niveau = ref('')
const afficherInactifs = ref(false)
const showFilters = ref(false)

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
  <div class="relative h-[calc(100vh-4rem)] w-full overflow-hidden bg-slate-100">
    
    <!-- Barre de recherche et filtres flottants (Top) -->
    <div class="absolute left-4 right-20 top-16 z-[1000] flex flex-col gap-2 sm:right-auto sm:top-4 sm:w-full sm:max-w-xl">
      <div class="flex items-center gap-2">
        <!-- Barre de recherche -->
        <div class="relative flex-1 shadow-md">
          <Search class="pointer-events-none absolute left-3 top-2.5 h-5 w-5 text-slate-400" />
          <input
            v-model="recherche"
            placeholder="Rechercher sur la carte..."
            class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm font-medium text-slate-700 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          />
        </div>
        
        <!-- Bouton Filtres -->
        <button 
          @click="showFilters = !showFilters"
          class="flex h-10 items-center justify-center gap-2 rounded-lg bg-white px-3 shadow-md sm:px-4 border border-slate-200 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
          :class="{ 'bg-blue-50 text-blue-600 border-blue-200': showFilters }"
        >
          <SlidersHorizontal class="h-4 w-4" />
          <span class="hidden sm:inline">Filtres</span>
        </button>
      </div>

      <!-- Panneau de filtres (Caché par défaut) -->
      <div v-if="showFilters" class="rounded-xl bg-white p-4 shadow-xl border border-slate-100 flex flex-col gap-3">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm font-semibold text-slate-800">Filtres avancés</span>
          <span class="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">{{ markers.length }} résultat(s)</span>
        </div>
        
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-500">Couleur des marqueurs</label>
            <select v-model="colorBy" class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm outline-none focus:border-blue-500">
              <option value="statut">Statut opérationnel</option>
              <option value="priorite">Priorité préventive</option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-500">Secteur</label>
            <select v-model="secteur" class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm outline-none focus:border-blue-500">
              <option value="">Tous</option>
              <option v-for="s in store.secteurs" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-500">Statut</label>
            <select v-model="statut" class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm outline-none focus:border-blue-500">
              <option value="">Tous</option>
              <option v-for="(label, value) in STATUT_OPERATIONNEL_LABELS" :key="value" :value="value">{{ label }}</option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-500">Priorité</label>
            <select v-model="niveau" class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm outline-none focus:border-blue-500">
              <option value="">Toutes</option>
              <option v-for="(label, value) in PRIORITE_LABELS" :key="value" :value="value">{{ label }}</option>
            </select>
          </div>
        </div>
        
        <label class="mt-2 flex cursor-pointer items-center gap-2 text-sm text-slate-700">
          <input v-model="afficherInactifs" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
          Afficher les transformateurs inactifs
        </label>
      </div>
    </div>

    <!-- Message d'erreur -->
    <p v-if="store.error" class="absolute top-20 left-1/2 z-[1000] -translate-x-1/2 rounded-lg bg-red-50 px-4 py-2 text-sm font-medium text-red-700 shadow-md">
      {{ store.error }}
    </p>

    <!-- Composant Carte (Plein écran) -->
    <TransformateurMap
      :markers="markers"
      :color-by="colorBy"
      @open="(id) => router.push(`/transformateurs/${id}`)"
    />
  </div>
</template>

<style scoped>
/* Assure que la carte prend bien tout l'espace disponible */
:deep(.leaflet-container) {
  height: 100%;
  width: 100%;
  z-index: 10;
}
</style>