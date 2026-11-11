<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Check, Copy, Crosshair, Maximize2, Minimize2 } from 'lucide-vue-next'

import { COULEURS_PRIORITE, COULEURS_STATUT } from '@/utils/couleurs'
import {
  ETAT_LABELS,
  PRIORITE_LABELS,
  STATUT_OPERATIONNEL_LABELS,
  formatDate,
  formatPourcent,
} from '@/utils/format'

const props = defineProps({
  markers: { type: Array, default: () => [] },
  colorBy: { type: String, default: 'statut' },
  zoom: { type: Number, default: 19 },
})
const emit = defineEmits(['open'])

const CENTRE_ANTSIRABE = [-19.8659, 47.0333]
const CLE_FOND = 'jirama_fond_carte'

const FONDS = {
  plan: {
    label: 'Plan',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    options: {
      maxZoom: 20,
      maxNativeZoom: 19,
      detectRetina: true,
      crossOrigin: true,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>',
    },
  },
  satellite: {
    label: 'Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    options: {
      maxZoom: 20,
      // ✅ CORRECTION : On s'arrête au zoom 16, dernier niveau fiable pour Antsirabe sur Esri.
      // Au-delà, Leaflet va étirer les tuiles du zoom 16 (rendu net grâce au CSS en bas).
      maxNativeZoom: 16, 
      detectRetina: true,
      crossOrigin: true,
      tileSize: 256,
      zoomOffset: 0,
      attribution:
        'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community',
    },
  },
}

function fondInitial() {
  try {
    const v = localStorage.getItem(CLE_FOND)
    return v && v in FONDS ? v : 'plan'
  } catch {
    return 'plan'
  }
}

const wrapper = ref(null)
const container = ref(null)
const fond = ref(fondInitial())
const chargement = ref(false)
const erreurTuiles = ref(false)
const centre = ref(null)
const copie = ref(false)
const pleinEcran = ref(false)
const pleinEcranDisponible = typeof document !== 'undefined' && !!document.fullscreenEnabled

let map = null
let layer = null
let tuiles = null
let tuilesFallback = null
let nbErreurs = 0
let derniereSignature = null
let observer = null
let timerCopie = null

// ---------------------------------------------------------------- marqueurs

function couleurDe(m) {
  if (props.colorBy === 'priorite') return COULEURS_PRIORITE[m.priorite] ?? '#64748b'
  return COULEURS_STATUT[m.statut_operationnel] ?? '#64748b'
}

function makeIcon(m) {
  const opacite = m.actif === false ? 0.5 : 1
  return L.divIcon({
    className: 'jirama-marker',
    html: `<span style="display:block;width:22px;height:22px;border-radius:9999px;background:${couleurDe(m)};border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.6);opacity:${opacite}"></span>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -12],
  })
}

function buildPopup(m) {
  const root = document.createElement('div')
  root.style.minWidth = '190px'

  const ligne = (texte, gras = false) => {
    const p = document.createElement('p')
    p.textContent = texte
    p.style.margin = '2px 0'
    if (gras) p.style.fontWeight = '700'
    root.appendChild(p)
  }

  ligne(m.reference, true)
  ligne(m.nom)
  if (m.secteur) ligne(`Quartier : ${m.secteur}`)
  ligne(`Puissance : ${m.puissance} kVA`)
  ligne(`Statut : ${STATUT_OPERATIONNEL_LABELS[m.statut_operationnel] ?? '—'}`)
  ligne(`Charge : ${formatPourcent(m.taux_charge)}`)
  ligne(`État technique : ${ETAT_LABELS[m.etat] ?? m.etat}`)
  ligne(`Priorité : ${PRIORITE_LABELS[m.priorite] ?? '—'}`)
  if (m.prochaine_inspection) ligne(`Prochaine inspection : ${formatDate(m.prochaine_inspection)}`)
  if (m.actif === false) ligne('(transformateur inactif)')

  const bouton = document.createElement('button')
  bouton.type = 'button'
  bouton.textContent = 'Voir le détail'
  bouton.style.cssText =
    'margin-top:6px;width:100%;cursor:pointer;border:0;border-radius:6px;background:#2563eb;color:#fff;padding:6px 10px;font-size:13px;font-weight:600'
  bouton.addEventListener('click', () => emit('open', m.id))
  root.appendChild(bouton)

  return root
}

function cadrer() {
  if (!map) return
  const points = props.markers.map((m) => [m.latitude, m.longitude])
  if (points.length === 1) map.setView(points[0], props.zoom)
  else if (points.length > 1) map.fitBounds(points, { padding: [40, 40] })
  else map.setView(CENTRE_ANTSIRABE, 13)
}

function draw() {
  if (!map) return
  layer.clearLayers()

  for (const m of props.markers) {
    L.marker([m.latitude, m.longitude], { icon: makeIcon(m) })
      .bindPopup(buildPopup(m))
      .addTo(layer)
  }

  const signature = props.markers.map((m) => m.id).sort((a, b) => a - b).join(',')
  if (signature !== derniereSignature) {
    derniereSignature = signature
    cadrer()
  }
}

// ---------------------------------------------------------------- fond de carte

function installerFond() {
  if (!map) return
  if (tuiles) {
    tuiles.off()
    map.removeLayer(tuiles)
  }
  if (tuilesFallback) {
    tuilesFallback.off()
    map.removeLayer(tuilesFallback)
    tuilesFallback = null
  }

  const f = FONDS[fond.value]
  nbErreurs = 0
  erreurTuiles.value = false

  tuiles = L.tileLayer(f.url, f.options)
  tuiles.on('loading', () => { chargement.value = true })
  tuiles.on('load', () => { chargement.value = false })
  tuiles.on('tileload', () => {
    nbErreurs = 0
    erreurTuiles.value = false
  })
  tuiles.on('tileerror', () => {
    nbErreurs += 1
    if (nbErreurs >= 4) {
      erreurTuiles.value = true
      // Fallback automatique : ajoute le plan OSM en dessous si le satellite échoue
      if (fond.value === 'satellite' && !tuilesFallback) {
        tuilesFallback = L.tileLayer(
          'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          { maxZoom: 19, opacity: 0.6 }
        )
        tuilesFallback.addTo(map)
        tuilesFallback.bringToBack()
      }
    }
  })
  tuiles.addTo(map)
}

function choisirFond(cle) {
  if (cle === fond.value) return
  fond.value = cle
  try {
    localStorage.setItem(CLE_FOND, cle)
  } catch {}
}

watch(fond, installerFond)

// ---------------------------------------------------------------- commandes

function basculerPleinEcran() {
  if (document.fullscreenElement) document.exitFullscreen()
  else wrapper.value?.requestFullscreen?.()
}

function surChangementPleinEcran() {
  pleinEcran.value = document.fullscreenElement === wrapper.value
  nextTick(() => {
    if (map) {
      map.invalidateSize()
      setTimeout(() => map && map.invalidateSize(), 200)
    }
  })
}

const centreTexte = computed(() =>
  centre.value ? `${centre.value.lat.toFixed(4)}, ${centre.value.lng.toFixed(4)}` : '',
)

async function copierCoordonnees() {
  try {
    await navigator.clipboard.writeText(centreTexte.value)
    copie.value = true
    clearTimeout(timerCopie)
    timerCopie = setTimeout(() => { copie.value = false }, 1500)
  } catch {}
}

const legende = computed(() => {
  const source = props.colorBy === 'priorite' ? COULEURS_PRIORITE : COULEURS_STATUT
  const labels = props.colorBy === 'priorite' ? PRIORITE_LABELS : STATUT_OPERATIONNEL_LABELS
  return Object.entries(source).map(([cle, couleur]) => ({ label: labels[cle], couleur }))
})

// ---------------------------------------------------------------- cycle de vie

onMounted(() => {
  map = L.map(container.value, {
    preferCanvas: false,
    zoomAnimation: true,
    fadeAnimation: true,
    markerZoomAnimation: true,
  }).setView(CENTRE_ANTSIRABE, 13)

  layer = L.layerGroup().addTo(map)
  map.on('moveend', () => { centre.value = map.getCenter() })

  installerFond()
  draw()
  centre.value = map.getCenter()

  observer = new ResizeObserver(() => map && map.invalidateSize())
  observer.observe(wrapper.value)
  document.addEventListener('fullscreenchange', surChangementPleinEcran)
})

watch(() => [props.markers, props.colorBy], draw, { deep: true })

onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', surChangementPleinEcran)
  clearTimeout(timerCopie)
  if (observer) observer.disconnect()
  if (tuiles) tuiles.off()
  if (tuilesFallback) tuilesFallback.off()
  if (map) { map.remove(); map = null }
})
</script>

<template>
  <div ref="wrapper" class="relative isolate h-full w-full overflow-hidden rounded-xl bg-slate-200">
    <div ref="container" class="absolute inset-0 z-0 map-sharp"></div>

    <!-- Fond de carte et commandes -->
    <div class="absolute right-3 top-3 z-[1000] flex flex-col items-end gap-2">
      <div class="flex overflow-hidden rounded-lg border border-slate-300 bg-white text-xs font-semibold shadow" role="group" aria-label="Fond de carte">
        <button
          v-for="(f, cle) in FONDS"
          :key="cle"
          type="button"
          class="cursor-pointer px-3 py-1.5 transition-colors"
          :class="fond === cle ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-100'"
          :aria-pressed="fond === cle"
          @click="choisirFond(cle)"
        >
          {{ f.label }}
        </button>
      </div>

      <button
        type="button"
        class="cursor-pointer rounded-lg border border-slate-300 bg-white p-2 text-slate-700 shadow hover:bg-slate-100"
        title="Recentrer sur les postes affichés"
        aria-label="Recentrer la carte"
        @click="cadrer"
      >
        <Crosshair class="h-4 w-4" />
      </button>

      <button
        v-if="pleinEcranDisponible"
        type="button"
        class="cursor-pointer rounded-lg border border-slate-300 bg-white p-2 text-slate-700 shadow hover:bg-slate-100"
        :title="pleinEcran ? 'Quitter le plein écran' : 'Plein écran'"
        :aria-label="pleinEcran ? 'Quitter le plein écran' : 'Plein écran'"
        @click="basculerPleinEcran"
      >
        <Minimize2 v-if="pleinEcran" class="h-4 w-4" />
        <Maximize2 v-else class="h-4 w-4" />
      </button>
    </div>

    <!-- Légende -->
    <div v-if="markers.length > 1" class="absolute bottom-7 left-3 z-[1000] rounded-lg bg-white/90 px-3 py-2 text-xs shadow">
      <p class="mb-1 font-semibold text-navy-900">{{ colorBy === 'priorite' ? 'Priorité' : 'Statut' }}</p>
      <p v-for="l in legende" :key="l.label" class="flex items-center gap-2 text-slate-700">
        <span class="inline-block h-3 w-3 rounded-full" :style="{ background: l.couleur }"></span>
        {{ l.label }}
      </p>
    </div>

    <!-- Coordonnées du centre de la carte, copiables -->
    <div v-if="centre" class="absolute bottom-7 right-3 z-[1000] flex items-center gap-2 rounded-md bg-white/90 px-2 py-1 font-mono text-xs text-slate-700 shadow" title="Coordonnées du centre de la carte">
      <span>{{ centreTexte }}</span>
      <button type="button" class="cursor-pointer rounded p-0.5 text-slate-500 hover:bg-slate-200" aria-label="Copier les coordonnées" @click="copierCoordonnees">
        <Check v-if="copie" class="h-3.5 w-3.5 text-green-600" />
        <Copy v-else class="h-3.5 w-3.5" />
      </button>
    </div>

    <!-- États du fond de carte -->
    <div v-if="erreurTuiles" class="absolute left-1/2 top-3 z-[1000] w-[90%] max-w-md -translate-x-1/2 rounded-lg border border-amber-300 bg-amber-50 px-4 py-2 text-sm text-amber-900 shadow" role="alert">
      Le fond de carte « {{ FONDS[fond].label }} » ne se charge pas (connexion ou service indisponible). Les postes restent affichés.
      <button type="button" class="ml-1 cursor-pointer font-semibold underline" @click="choisirFond(fond === 'plan' ? 'satellite' : 'plan')">
        Essayer l'autre fond
      </button>
    </div>
    <div v-else-if="chargement" class="pointer-events-none absolute left-1/2 top-3 z-[1000] -translate-x-1/2 rounded-full bg-white/90 px-3 py-1 text-xs text-slate-600 shadow">
      Chargement de la carte...
    </div>
  </div>
</template>

<style>
/* =========================================================================
   CORRECTION DU FLOU : Force le navigateur à ne PAS lisser les images
   de tuiles lors de l'upscale (quand on dépasse le maxNativeZoom).
   ========================================================================= */
.map-sharp .leaflet-tile {
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  image-rendering: pixelated;
  -ms-interpolation-mode: nearest-neighbor;
}

/* Sur les tuiles "retina" (2x), on n'applique pas le pixelated car elles sont déjà haute résolution */
.map-sharp .leaflet-tile.leaflet-tile-loaded[src*="2x"],
.map-sharp .leaflet-tile.leaflet-tile-loaded[src*="@2x"] {
  image-rendering: auto;
  -ms-interpolation-mode: auto;
}

/* Empêche l'anti-aliasing forcé qui crée du flou sur les popups */
.leaflet-popup-content {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>