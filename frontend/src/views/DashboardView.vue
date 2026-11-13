<script setup>
import { computed, onMounted } from 'vue'
import {
  Activity,
  CalendarClock,
  Check,
  CheckCircle2,
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
import ChargeGauge from '@/components/dashboard/ChargeGauge.vue'
import EtatsDonut from '@/components/dashboard/EtatsDonut.vue'
import PrioritesTable from '@/components/dashboard/PrioritesTable.vue'
import ProchainesInspections from '@/components/dashboard/ProchainesInspections.vue'
import RepartitionChart from '@/components/dashboard/RepartitionChart.vue'
import SecteursTable from '@/components/dashboard/SecteursTable.vue'
import StatutsChart from '@/components/dashboard/StatutsChart.vue'
import { useAuthStore } from '@/stores/authStore'
import { useDashboardStore } from '@/stores/dashboardStore'
import { formatMontant, formatPourcent } from '@/utils/format'

const auth = useAuthStore()

// Date du jour affichée dans l'en-tête (elle était écrite en dur : 03/11/2025).
const dateAujourdhui = new Date().toLocaleDateString('fr-FR')
const dashboard = useDashboardStore()

const stats = computed(() => dashboard.statistics)

// Vérification si le backend renvoie bien toutes les nouvelles stats
const backendAJour = computed(
  () => !!stats.value && !!stats.value.repartition_statuts && Array.isArray(stats.value.repartition_secteurs),
)

function part(n) {
  const total = stats.value?.total_transformateurs
  return total ? formatPourcent((n / total) * 100) : '0%'
}

// Les 4 cartes KPI principales (Design identique à la maquette)
const kpis = computed(() => {
  const s = stats.value
  if (!s) return []
  return [
    { 
      label: 'Total', 
      value: s.total_transformateurs, 
      subtitle: 'Transformateurs', 
      icon: Zap, 
      iconColor: 'text-blue-600', 
      iconBg: 'bg-blue-100' 
    },
    { 
      label: 'Opérationnels', 
      value: s.transformateurs_bon, 
      subtitle: `(${part(s.transformateurs_bon)} des actifs)`, 
      icon: CheckCircle2, 
      iconColor: 'text-green-600', 
      iconBg: 'bg-green-100' 
    },
    { 
      label: 'En panne', 
      value: s.transformateurs_critiques, 
      subtitle: `(${part(s.transformateurs_critiques)} des actifs)`, 
      icon: ShieldAlert, 
      iconColor: 'text-red-600', 
      iconBg: 'bg-red-100' 
    },
    { 
      label: 'À inspecter', 
      value: s.transformateurs_a_surveiller, 
      subtitle: `(${part(s.transformateurs_a_surveiller)} des actifs)`, 
      icon: Eye, 
      iconColor: 'text-orange-500', 
      iconBg: 'bg-orange-100' 
    },
  ]
})

// Les indicateurs détaillés (Section secondaire)
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

onMounted(() => {
  dashboard.fetchAll(auth.canViewStatistics)
})
</script>

<template>
  <div class="space-y-6 pb-10">
    
    <!-- En-tête avec filtres -->
    <header class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">Tableau de bord</h2>
        <p class="text-sm text-slate-500">Vue d'ensemble du réseau de distribution</p>
      </div>
      
      <!-- Date du jour (le sélecteur de zone décoratif a été retiré : il ne filtrait rien) -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700">
          <CalendarClock class="h-4 w-4 text-slate-400" />
          <span>{{ dateAujourdhui }}</span>
        </div>
      </div>
    </header>

    <!-- Erreurs et chargement -->
    <p v-if="dashboard.error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ dashboard.error }}
    </p>
    <p v-else-if="dashboard.loading && !stats" class="text-sm text-slate-500 flex items-center gap-2">
      <Loader class="h-4 w-4 animate-spin" /> Chargement des données...
    </p>

    <p v-if="stats && !backendAJour" class="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800 border border-amber-200">
      Le backend ne renvoie pas les nouvelles statistiques. Vérifiez que les fichiers de l'étape 12 sont appliqués.
    </p>

    <!-- 4 CARTES KPI PRINCIPALES -->
    <section v-if="auth.canViewStatistics && stats" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div 
        v-for="k in kpis" 
        :key="k.label"
        class="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      >
        <div>
          <p class="text-sm font-medium text-slate-500 mb-1">{{ k.label }}</p>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-bold text-slate-800">{{ k.value }}</span>
          </div>
          <p class="text-xs text-slate-400 mt-1">{{ k.subtitle }}</p>
        </div>
        <div :class="[k.iconBg, 'flex h-12 w-12 items-center justify-center rounded-full']">
          <component :is="k.icon" :class="[k.iconColor, 'h-6 w-6']" />
        </div>
      </div>
    </section>

    <p v-else-if="!auth.canViewStatistics" class="rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-800">
      Votre profil (agent) donne accès aux priorités préventives. Les statistiques globales sont réservées aux administrateurs.
    </p>

    <!-- SECTION GRAPHIQUES & INSPECTIONS (Design Maquette) -->
    <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      
      <!-- Graphique d'évolution (2/3) -->
      <div class="flex flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-base font-semibold text-slate-800">Activité mensuelle</h3>
          <!-- Légende : elle correspond aux séries réellement tracées (inspections / interventions) -->
          <div class="flex items-center gap-4 text-xs font-medium text-slate-600">
            <div class="flex items-center gap-1.5"><div class="h-2 w-2 rounded-full bg-blue-500"></div> Inspections</div>
            <div class="flex items-center gap-1.5"><div class="h-2 w-2 rounded-full bg-amber-500"></div> Interventions</div>
          </div>
        </div>
        <div class="relative min-h-[16rem] flex-1">
          <!-- Si ActiviteChart n'est pas un LineChart, remplacez-le par votre composant Chart.js -->
          <ActiviteChart v-if="stats?.activite_mensuelle" :activite="stats.activite_mensuelle" />
          <div v-else class="flex h-full items-center justify-center text-sm text-slate-400">Aucune donnée disponible</div>
        </div>
      </div>

      <!-- Liste des prochaines inspections (1/3) -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-base font-semibold text-slate-800">Prochaines inspections</h3>
          <RouterLink to="/inspections" class="text-xs font-medium text-blue-600 hover:underline">Voir tout →</RouterLink>
        </div>
        <div class="max-h-[28rem] overflow-y-auto pr-1">
          <ProchainesInspections :data="dashboard.upcoming" :loading="dashboard.loading" />
        </div>
      </div>
    </section>

    <!-- SECTION SECONDAIRE : Détails, Donut, Charge, Tableaux -->
    <template v-if="auth.canViewStatistics && stats">
      
      <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Donut États -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-slate-800">État des transformateurs</h3>
          <EtatsDonut
            :bon="stats.transformateurs_bon"
            :surveiller="stats.transformateurs_a_surveiller"
            :critique="stats.transformateurs_critiques"
          />
        </div>
        
        <!-- Jauge Charge -->
        <div v-if="backendAJour" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-slate-800">Taux de charge moyen</h3>
          <ChargeGauge :taux="stats.taux_charge_moyen" />
        </div>

        <!-- Statuts Chart -->
        <div v-if="backendAJour" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-slate-800">Statut opérationnel</h3>
          <StatutsChart :repartition="stats.repartition_statuts" />
        </div>
      </section>

      <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Répartition Priorités -->
        <div v-if="stats.repartition_priorites" class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 text-sm font-semibold text-slate-800">Répartition des priorités</h3>
          <RepartitionChart :repartition="stats.repartition_priorites" />
        </div>
        
        <!-- Synthèse Secteurs -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
          <h3 class="mb-3 text-sm font-semibold text-slate-800">Synthèse par quartier</h3>
          <SecteursTable :secteurs="stats.repartition_secteurs" />
        </div>
      </section>

      <!-- Indicateurs détaillés -->
      <section>
        <h3 class="mb-3 text-sm font-semibold text-slate-800">Indicateurs détaillés</h3>
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
        <p class="mt-4 text-sm text-slate-500 bg-white p-3 rounded-lg border border-slate-200 inline-block">
          Coût total des interventions terminées :
          <span class="font-bold text-slate-800">{{ formatMontant(stats.cout_total_interventions_terminees) }}</span>
        </p>
      </section>
    </template>

    <!-- PRIORITÉS (Tous les rôles) -->
    <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="mb-3 text-sm font-semibold text-slate-800">Transformateurs à traiter en priorité</h3>
      <PrioritesTable :items="dashboard.priorities" />
    </section>
  </div>
</template>