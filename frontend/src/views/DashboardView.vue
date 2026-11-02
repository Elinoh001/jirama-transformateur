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
import { useRouter } from 'vue-router'

import KpiCard from '@/components/common/KpiCard.vue'
import StatCard from '@/components/common/StatCard.vue'
import ActiviteChart from '@/components/dashboard/ActiviteChart.vue'
import ChargeGauge from '@/components/dashboard/ChargeGauge.vue'
import EtatsDonut from '@/components/dashboard/EtatsDonut.vue'
import PrioritesTable from '@/components/dashboard/PrioritesTable.vue'
import ProchainesInspections from '@/components/dashboard/ProchainesInspections.vue'
import RepartitionChart from '@/components/dashboard/RepartitionChart.vue'
import SecteursTable from '@/components/dashboard/SecteursTable.vue'
import StatutsChart from '@/components/dashboard/StatutsChart.vue'
import TransformateurMap from '@/components/map/TransformateurMap.vue'
import { useAuthStore } from '@/stores/authStore'
import { useDashboardStore } from '@/stores/dashboardStore'
import { useTransformateurStore } from '@/stores/transformateurStore'
import { formatMontant, formatPourcent } from '@/utils/format'

const router = useRouter()
const auth = useAuthStore()
const dashboard = useDashboardStore()
const transformateurs = useTransformateurStore()

const stats = computed(() => dashboard.statistics)

// Champs ajoutés à l'étape 12 : si le backend n'est pas à jour, on avertit au lieu de planter.
const backendAJour = computed(
  () => !!stats.value && !!stats.value.repartition_statuts && Array.isArray(stats.value.repartition_secteurs),
)

function part(n) {
  const total = stats.value?.total_transformateurs
  return total ? formatPourcent((n / total) * 100) : '—'
}

// 4 grandes cartes (total, bon, à surveiller, critiques)
const kpis = computed(() => {
  const s = stats.value
  if (!s) return []
  return [
    { label: 'Total transformateurs', value: s.total_transformateurs, subtitle: `${s.transformateurs_actifs} actifs`, icon: Zap, tone: 'blue' },
    { label: 'En bon état', value: s.transformateurs_bon, subtitle: part(s.transformateurs_bon), icon: ShieldCheck, tone: 'green' },
    { label: 'À surveiller', value: s.transformateurs_a_surveiller, subtitle: part(s.transformateurs_a_surveiller), icon: Eye, tone: 'amber' },
    { label: 'Critiques', value: s.transformateurs_critiques, subtitle: part(s.transformateurs_critiques), icon: ShieldAlert, tone: 'red' },
  ]
})

// Les 12 autres indicateurs (cahier des charges et PRD)
const cartes = computed(() => {
  const s = stats.value
  if (!s) return []
  const base = [
    { label: 'Actifs', value: s.transformateurs_actifs, icon: Power, tone: 'green' },
    { label: 'Inactifs', value: s.transformateurs_inactifs, icon: PowerOff, tone: 'slate' },
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

const postesActifs = computed(() => transformateurs.items.filter((t) => t.actif))

onMounted(() => {
  dashboard.fetchAll(auth.canViewStatistics)
  transformateurs.fetchAll()
})
</script>

<template>
  <div class="space-y-6">
    <header>
      <h2 class="text-2xl font-bold text-navy-900">Bonjour, {{ auth.fullName }}</h2>
      <p class="text-sm text-slate-600">Voici un aperçu de l'état de votre réseau de transformateurs.</p>
    </header>

    <p v-if="dashboard.error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ dashboard.error }}
    </p>

    <p v-else-if="dashboard.loading && !stats && dashboard.priorities.length === 0" class="text-sm text-slate-500">
      Chargement...
    </p>

    <p v-if="stats && !backendAJour" class="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
      Le backend ne renvoie pas les nouvelles statistiques (statuts, charge, pannes, secteurs).
      Vérifiez que les fichiers de l'étape 12 sont appliqués, puis redémarrez uvicorn.
    </p>

    <!-- 4 indicateurs principaux -->
    <section v-if="auth.canViewStatistics && stats" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard
        v-for="k in kpis"
        :key="k.label"
        :label="k.label"
        :value="k.value"
        :subtitle="k.subtitle"
        :icon="k.icon"
        :tone="k.tone"
        to="/transformateurs"
      />
    </section>

    <p
      v-else-if="!auth.canViewStatistics"
      class="rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-800"
    >
      Votre profil (agent) donne accès aux priorités préventives. Les statistiques globales sont réservées
      aux administrateurs et superviseurs.
    </p>

    <!-- Carte et prochaines inspections -->
    <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-navy-900">Localisation des transformateurs</h3>
          <RouterLink to="/carte" class="text-sm font-medium text-blue-600 hover:underline">Ouvrir la carte →</RouterLink>
        </div>
        <div class="h-80">
          <TransformateurMap
            :markers="postesActifs"
            @open="(id) => router.push(`/transformateurs/${id}`)"
          />
        </div>
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-navy-900">Prochaines inspections</h3>
          <RouterLink to="/inspections" class="text-sm font-medium text-blue-600 hover:underline">Voir tout →</RouterLink>
        </div>
        <ProchainesInspections :data="dashboard.upcoming" :loading="dashboard.loading" />
      </div>
    </section>

    <!-- Graphiques (ADMIN et SUPERVISEUR) -->
    <template v-if="auth.canViewStatistics && stats">
      <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-navy-900">État des transformateurs</h3>
          <EtatsDonut
            :bon="stats.transformateurs_bon"
            :surveiller="stats.transformateurs_a_surveiller"
            :critique="stats.transformateurs_critiques"
          />
        </div>
        <div v-if="stats.activite_mensuelle" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-navy-900">Activité des 6 derniers mois</h3>
          <ActiviteChart :activite="stats.activite_mensuelle" />
        </div>
        <div v-if="backendAJour" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-navy-900">Taux de charge moyen</h3>
          <ChargeGauge :taux="stats.taux_charge_moyen" />
        </div>
      </section>

      <section v-if="backendAJour" class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-navy-900">Statut opérationnel des postes actifs</h3>
          <StatutsChart :repartition="stats.repartition_statuts" />
        </div>
        <div v-if="stats.repartition_priorites" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-navy-900">Répartition des priorités</h3>
          <RepartitionChart :repartition="stats.repartition_priorites" />
        </div>
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-3 text-sm font-semibold text-navy-900">Synthèse par quartier</h3>
          <SecteursTable :secteurs="stats.repartition_secteurs" />
        </div>
      </section>

      <section>
        <h3 class="mb-3 text-sm font-semibold text-navy-900">Indicateurs détaillés</h3>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            v-for="carte in cartes"
            :key="carte.label"
            :label="carte.label"
            :value="carte.value"
            :icon="carte.icon"
            :tone="carte.tone"
          />
        </div>
        <p class="mt-3 text-sm text-slate-500">
          Coût des interventions terminées :
          <span class="font-semibold text-navy-900">{{ formatMontant(stats.cout_total_interventions_terminees) }}</span>
        </p>
      </section>
    </template>

    <!-- Priorités (tous les rôles) -->
    <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="mb-3 text-sm font-semibold text-navy-900">Transformateurs à traiter en priorité</h3>
      <PrioritesTable :items="dashboard.priorities" />
    </section>
  </div>
</template>