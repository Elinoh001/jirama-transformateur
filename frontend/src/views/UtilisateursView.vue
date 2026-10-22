<script setup>
import { onMounted, ref } from 'vue'
import { Pencil, Plus, Trash2 } from 'lucide-vue-next'

import AppModal from '@/components/common/AppModal.vue'
import UtilisateurForm from '@/components/users/UtilisateurForm.vue'
import { getErrorMessage } from '@/services/api'
import utilisateurService from '@/services/utilisateurService'
import { useAuthStore } from '@/stores/authStore'
import { ROLE_LABELS, formatDate } from '@/utils/format'
import { btnIcon, btnIconDanger, btnPrimary, cardClass, thClass } from '@/utils/ui'

const auth = useAuthStore()

const utilisateurs = ref([])
const loading = ref(false)
const error = ref('')

const showForm = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')

const ROLE_CLASSES = {
  ADMIN: 'bg-purple-100 text-purple-800',
  SUPERVISEUR: 'bg-blue-100 text-blue-800',
  AGENT: 'bg-slate-100 text-slate-700',
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    utilisateurs.value = await utilisateurService.list()
  } catch (e) {
    error.value = getErrorMessage(e, 'Impossible de charger les utilisateurs')
  } finally {
    loading.value = false
  }
}

onMounted(load)

function ouvrirCreation() {
  editing.value = null
  formError.value = ''
  showForm.value = true
}

function ouvrirEdition(u) {
  editing.value = u
  formError.value = ''
  showForm.value = true
}

async function enregistrer(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await utilisateurService.update(editing.value.id, payload)
    } else {
      await utilisateurService.create(payload)
    }
    showForm.value = false
    await load()
  } catch (e) {
    formError.value = getErrorMessage(e, "Impossible d'enregistrer l'utilisateur")
  } finally {
    saving.value = false
  }
}

async function supprimer(u) {
  if (!window.confirm(`Supprimer l'utilisateur ${u.prenom} ${u.nom} (${u.email}) ?`)) return
  error.value = ''
  try {
    await utilisateurService.remove(u.id)
    await load()
  } catch (e) {
    error.value = getErrorMessage(e, 'Suppression impossible')
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <p class="text-sm text-slate-500">{{ utilisateurs.length }} utilisateur(s)</p>
      <button type="button" :class="btnPrimary" @click="ouvrirCreation">
        <Plus class="h-4 w-4" /> Nouvel utilisateur
      </button>
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>

    <div :class="[cardClass, 'overflow-x-auto']">
      <table class="min-w-full text-sm">
        <thead class="border-b border-slate-200 bg-slate-50">
          <tr>
            <th :class="thClass">Nom</th>
            <th :class="thClass">Email</th>
            <th :class="thClass">Rôle</th>
            <th :class="thClass">Statut</th>
            <th :class="thClass">Créé le</th>
            <th :class="[thClass, 'text-right']">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="loading && utilisateurs.length === 0">
            <td colspan="6" class="px-3 py-8 text-center text-slate-500">Chargement...</td>
          </tr>
          <tr v-for="u in utilisateurs" :key="u.id" class="hover:bg-slate-50">
            <td class="px-3 py-3 font-medium">
              {{ u.prenom }} {{ u.nom }}
              <span v-if="u.id === auth.user?.id" class="ml-1 text-xs font-normal text-slate-400">(vous)</span>
            </td>
            <td class="px-3 py-3 text-slate-600">{{ u.email }}</td>
            <td class="px-3 py-3">
              <span
                class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold"
                :class="ROLE_CLASSES[u.role]"
              >
                {{ ROLE_LABELS[u.role] }}
              </span>
            </td>
            <td class="px-3 py-3">
              <span :class="u.actif ? 'text-green-700' : 'text-slate-400'">{{ u.actif ? 'Actif' : 'Désactivé' }}</span>
            </td>
            <td class="whitespace-nowrap px-3 py-3 text-slate-600">{{ formatDate(u.created_at) }}</td>
            <td class="whitespace-nowrap px-3 py-3 text-right">
              <button type="button" :class="btnIcon" title="Modifier" @click="ouvrirEdition(u)">
                <Pencil class="h-4 w-4" />
              </button>
              <button
                v-if="u.id !== auth.user?.id"
                type="button"
                :class="btnIconDanger"
                title="Supprimer"
                @click="supprimer(u)"
              >
                <Trash2 class="h-4 w-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppModal
      :open="showForm"
      :title="editing ? `Modifier ${editing.prenom} ${editing.nom}` : 'Nouvel utilisateur'"
      wide
      @close="showForm = false"
    >
      <UtilisateurForm
        :utilisateur="editing"
        :saving="saving"
        :error="formError"
        @submit="enregistrer"
        @cancel="showForm = false"
      />
    </AppModal>
  </div>
</template>