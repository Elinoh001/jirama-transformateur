<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import { COULEURS_PRIORITE, COULEURS_STATUT } from '@/utils/couleurs'
import {
  ETAT_LABELS,
  PRIORITE_LABELS,
  STATUT_OPERATIONNEL_LABELS,
  formatPourcent,
} from '@/utils/format'

const props = defineProps({
  markers: { type: Array, default: () => [] },
  colorBy: { type: String, default: 'statut' },
  zoom: { type: Number, default: 14 },
})
const emit = defineEmits(['open'])

const container = ref(null)
let map = null
let markerLayer = null
let resizeObserver = null

const CENTRE_ANTSIRABE = [-19.8659, 47.0333]
const ATTRIBUTION_ESRI = 'Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community'
const ATTRIBUTION_OSM = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

function couleurDe(m) {
  if (props.colorBy === 'priorite') return COULEURS_PRIORITE[m.priorite] ?? '#64748b'
  return COULEURS_STATUT[m.statut_operationnel] ?? '#64748b'
}

function makeIcon(m) {
  const color = couleurDe(m)
  const opacity = m.actif === false ? 0.48 : 1
  return L.divIcon({
    className: 'jirama-marker',
    html: `<span style="display:block;width:20px;height:20px;border-radius:50%;background:${color};border:3px solid #fff;box-shadow:0 2px 8px rgba(15,23,42,.55);opacity:${opacity}"></span>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -12],
  })
}

// Les valeurs provenant de l'API sont insérées avec textContent, jamais comme HTML.
function buildPopup(m) {
  const root = document.createElement('div')
  root.className = 'jirama-map-popup'
  root.style.minWidth = '190px'

  const title = document.createElement('strong')
  title.textContent = m.reference || 'Transformateur'
  title.style.display = 'block'
  title.style.marginBottom = '6px'
  root.appendChild(title)

  const ligne = (label, value) => {
    const p = document.createElement('p')
    p.textContent = `${label} : ${value ?? '—'}`
    p.style.margin = '3px 0'
    root.appendChild(p)
  }

  ligne('Nom', m.nom)
  if (m.secteur) ligne('Secteur', m.secteur)
  ligne('Puissance', m.puissance != null ? `${m.puissance} kVA` : '—')
  ligne('Statut', STATUT_OPERATIONNEL_LABELS[m.statut_operationnel] ?? '—')
  ligne('Charge', formatPourcent(m.taux_charge))
  ligne('État technique', ETAT_LABELS[m.etat] ?? m.etat)
  ligne('Priorité', PRIORITE_LABELS[m.priorite] ?? '—')
  if (m.actif === false) ligne('Disponibilité', 'Inactif')

  const button = document.createElement('button')
  button.type = 'button'
  button.textContent = 'Ouvrir la fiche technique'
  button.style.cssText = 'margin-top:9px;width:100%;cursor:pointer;border:0;border-radius:8px;background:#0f766e;color:#fff;padding:9px 11px;font-size:12px;font-weight:700'
  button.addEventListener('click', () => emit('open', m.id))
  root.appendChild(button)
  return root
}

function validCoordinates(m) {
  const lat = Number(m.latitude)
  const lng = Number(m.longitude)
  return Number.isFinite(lat) && Number.isFinite(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180
}

function drawMarkers() {
  if (!map || !markerLayer) return
  markerLayer.clearLayers()

  const points = []
  for (const item of props.markers) {
    if (!validCoordinates(item)) continue
    const point = [Number(item.latitude), Number(item.longitude)]
    points.push(point)
    L.marker(point, { icon: makeIcon(item), title: item.reference || item.nom || 'Transformateur' })
      .bindPopup(buildPopup(item), { maxWidth: 280 })
      .addTo(markerLayer)
  }

  if (points.length === 1) {
    map.flyTo(points[0], Math.max(props.zoom, 16), { duration: 0.65 })
  } else if (points.length > 1) {
    map.fitBounds(L.latLngBounds(points), { padding: [48, 48], maxZoom: 16, animate: true })
  } else {
    map.setView(CENTRE_ANTSIRABE, 13)
  }
}

onMounted(() => {
  map = L.map(container.value, {
    zoomControl: true,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    wheelPxPerZoomLevel: 90,
    preferCanvas: true,
  }).setView(CENTRE_ANTSIRABE, 13)

  // Imagerie satellite Esri. maxNativeZoom évite de prétendre qu'une image
  // interpolée au-delà de la résolution disponible contient plus de détails.
  const satellite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: ATTRIBUTION_ESRI, maxNativeZoom: 19, maxZoom: 22, keepBuffer: 4 }
  )
  const streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: ATTRIBUTION_OSM,
    maxNativeZoom: 19,
    maxZoom: 22,
    subdomains: 'abc',
    keepBuffer: 4,
  })

  satellite.addTo(map)
  L.control.layers(
    { 'Satellite': satellite, 'Plan de rues': streets },
    {},
    { position: 'topright', collapsed: false }
  ).addTo(map)

  markerLayer = L.layerGroup().addTo(map)
  drawMarkers()

  // Leaflet doit recalculer sa surface lorsque le panneau change de taille.
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => map?.invalidateSize({ pan: false, debounceMoveend: true }))
    resizeObserver.observe(container.value)
  }
  requestAnimationFrame(() => map?.invalidateSize({ pan: false }))
})

watch(() => [props.markers, props.colorBy], drawMarkers, { deep: true })

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
  if (map) {
    map.remove()
    map = null
    markerLayer = null
  }
})
</script>

<template>
  <div ref="container" class="jirama-leaflet-map relative z-0 h-full w-full rounded-xl" aria-label="Carte de localisation des transformateurs"></div>
</template>

<style>
.jirama-leaflet-map { min-height: 360px; background: #e2e8f0; }
.jirama-leaflet-map .leaflet-control-layers {
  border: 1px solid rgba(148, 163, 184, .35);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, .16);
  color: #0f172a;
  font: 600 12px/1.5 Inter, ui-sans-serif, system-ui, sans-serif;
}
.jirama-leaflet-map .leaflet-control-zoom a {
  color: #0f172a;
  border-color: #e2e8f0;
}
.jirama-leaflet-map .leaflet-popup-content-wrapper {
  border-radius: 12px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, .18);
}
.jirama-leaflet-map .leaflet-popup-content {
  margin: 13px 15px;
  font: 12px/1.55 Inter, ui-sans-serif, system-ui, sans-serif;
  color: #334155;
}
.jirama-leaflet-map .leaflet-popup-content strong { color: #0f172a; font-size: 13px; }
.jirama-leaflet-map .leaflet-control-attribution { font-size: 10px; }
</style>
