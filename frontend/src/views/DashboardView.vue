<script setup>
import { computed, onMounted } from 'vue'
import {
  Activity,
  CalendarClock,
  Check,
  ClipboardCheck,
  Eye,
  Flag,
  Gauge,
  Loader,
  Power,
  PowerOff,
  ShieldAlert,
  ShieldCheck,
  Wrench,
  Zap,
} from 'lucide-vue-next'

import StatCard from '@/components/common/StatCard.vue'
import ActiviteChart from '@/components/dashboard/ActiviteChart.vue'
import PrioritesTable from '@/components/dashboard/PrioritesTable.vue'
import RepartitionChart from '@/components/dashboard/RepartitionChart.vue'
import SecteursTable from '@/components/dashboard/SecteursTable.vue'
import StatutsChart from '@/components/dashboard/StatutsChart.vue'
import { useAuthStore } from '@/stores/authStore'
import { useDashboardStore } from '@/stores/dashboardStore'
import { formatMontant, formatPourcent } from '@/utils/format'

const auth = useAuthStore()
const dashboard = useDashboardStore()

const stats = computed(() => dashboard.statistics)

// Champs ajoutés à l'étape 12 : si le backend n'est pas à jour, on avertit au lieu de planter.
const backendAJour = computed(
  () => !!stats.value && !!stats.value.repartition_statuts && Array.isArray(stats.value.repartition_secteurs),
)

// Les 12 indicateurs du cahier des charges, puis 4 indicateurs du PRD (charge et pannes).
const cartes = computed(() => {
  const s = stats.value
  if (!s) return []
  const base = [
    { label: 'Transformateurs', value: s.total_transformateurs, icon: Zap, tone: 'blue' },
    { label: 'Actifs', value: s.transformateurs_actifs, icon: Power, tone: 'green' },
    { label: 'Inactifs', value: s.transformateurs_inactifs, icon: PowerOff, tone: 'slate' },
    { label: 'En bon état', value: s.transformateurs_bon, icon: ShieldCheck, tone: 'green' },
    { label: 'À surveiller', value: s.transformateurs_a_surveiller, icon: Eye, tone: 'amber' },
    { label: 'Critiques', value: s.transformateurs_critiques, icon: ShieldAlert, tone: 'red' },
    { label: 'Inspections', value: s.total_inspections, icon: ClipboardCheck, tone: 'blue' },
    { label: 'Interventions', value: s.total_interventions, icon: Wrench, tone: 'blue' },
    { label: 'Interv. planifiées', value: s.interventions_planifiees, icon: CalendarClock, tone: 'slate' },
    { label: 'Interv. en cours', value: s.interventions_en_cours, icon: Loader, tone: 'amber' },
    { label: 'Interv. terminées', value: s.interventions_terminees, icon: Check, tone: 'green' },
    { label: 'Priorités', value: s.nb_priorites, icon: Flag, tone: 'red' },
  ]
  if (!backendAJour.value) return base
  return [
    ...base,
    { label: 'Charge moyenne', value: formatPourcent(s.taux_charge_moyen), icon: Gauge, tone: 'blue' },
    { label: 'Postes en surcharge', value: s.postes_en_surcharge, icon: Activity, tone: 'amber' },
    { label: 'Pannes actives', value: s.pannes_actives, icon: ShieldAlert, tone: 'amber' },
    { label: 'Pannes critiques', value: s.pannes_critiques_actives, icon: ShieldAlert, tone: 'red' },
  ]
})

onMounted(() => {
  dashboard.fetchAll(auth.canViewStatistics)
})
</script>

<template>
  <div class="space-y-6">
    <p v-if="dashboard.error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ dashboard.error }}
    </p>

    <p v-else-if="dashboard.loading && !stats && dashboard.priorities.length === 0" class="text-sm text-slate-500">
      Chargement...
    </p>

    <template v-if="auth.canViewStatistics && stats">
      <p v-if="!backendAJour" class="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Le backend ne renvoie pas les nouvelles statistiques (statuts, charge, pannes, secteurs).
        Vérifiez que les fichiers de l'étape 12 sont appliqués, puis redémarrez uvicorn.
      </p>

      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          v-for="carte in cartes"
          :key="carte.label"
          :label="carte.label"
          :value="carte.value"
          :icon="carte.icon"
          :tone="carte.tone"
        />
      </section>

      <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div v-if="stats.repartition_statuts" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-4 text-sm font-semibold text-slate-700">Statut opérationnel des postes actifs</h2>
          <StatutsChart :repartition="stats.repartition_statuts" />
        </div>
        <div v-if="stats.repartition_priorites" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-4 text-sm font-semibold text-slate-700">Répartition des priorités</h2>
          <RepartitionChart :repartition="stats.repartition_priorites" />
        </div>
        <div v-if="stats.activite_mensuelle" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-4 text-sm font-semibold text-slate-700">Activité des 6 derniers mois</h2>
          <ActiviteChart :activite="stats.activite_mensuelle" />
        </div>
      </section>

      <section v-if="stats.repartition_secteurs" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 class="mb-3 text-sm font-semibold text-slate-700">Synthèse par secteur / quartier</h2>
        <SecteursTable :secteurs="stats.repartition_secteurs" />
      </section>

      <p class="text-sm text-slate-500">
        Coût des interventions terminées :
        <span class="font-semibold text-slate-800">{{ formatMontant(stats.cout_total_interventions_terminees) }}</span>
      </p>
    </template>

    <p
      v-else-if="!auth.canViewStatistics"
      class="rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-800"
    >
      Votre profil (agent) donne accès aux priorités préventives. Les statistiques globales sont réservées
      aux administrateurs et superviseurs.
    </p>

    <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 class="mb-3 text-sm font-semibold text-slate-700">Transformateurs à traiter en priorité</h2>
      <PrioritesTable :items="dashboard.priorities" />
    </section>
  </div>
</template>