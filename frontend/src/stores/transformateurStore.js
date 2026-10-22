import { ref } from 'vue'
import { defineStore } from 'pinia'

import transformateurService from '@/services/transformateurService'
import { getErrorMessage } from '@/services/api'

export const useTransformateurStore = defineStore('transformateur', () => {
  const items = ref([])
  const secteurs = ref([])
  const loading = ref(false)
  const error = ref('')
  let derniersParams = {}

  async function fetchAll(params = {}) {
    derniersParams = params
    loading.value = true
    error.value = ''
    try {
      items.value = await transformateurService.list(params)
    } catch (e) {
      error.value = getErrorMessage(e, 'Impossible de charger les transformateurs')
    } finally {
      loading.value = false
    }
  }

  /** Liste des secteurs valides (chargée une seule fois). */
  async function fetchSecteurs() {
    if (secteurs.value.length > 0) return
    try {
      secteurs.value = await transformateurService.secteurs()
    } catch {
      // Les formulaires afficheront simplement une liste vide.
    }
  }

  // Les erreurs de create/update/remove sont gérées par la vue appelante.
  async function create(payload) {
    const t = await transformateurService.create(payload)
    await fetchAll(derniersParams)
    return t
  }

  async function update(id, payload) {
    const t = await transformateurService.update(id, payload)
    await fetchAll(derniersParams)
    return t
  }

  async function remove(id) {
    await transformateurService.remove(id)
    await fetchAll(derniersParams)
  }

  return { items, secteurs, loading, error, fetchAll, fetchSecteurs, create, update, remove }
})