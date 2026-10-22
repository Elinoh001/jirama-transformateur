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
  // Objets transformateur (API) : id, reference, nom, secteur, puissance, etat, actif,
  // latitude, longitude, statut_operationnel, taux_charge, priorite
  markers: { type: Array, default: () => [] },
  colorBy: { type: String, default: 'statut' }, // 'statut' | 'priorite'
  zoom: { type: Number, default: 14 }, // zoom utilisé quand il n'y a qu'un seul marqueur
})
const emit = defineEmits(['open'])

const container = ref(null)
let map = null
let layer = null

const CENTRE_ANTSIRABE = [-19.8659, 47.0333]

function couleurDe(m) {
  if (props.colorBy === 'priorite') return COULEURS_PRIORITE[m.priorite] ?? '#64748b'
  return COULEURS_STATUT[m.statut_operationnel] ?? '#64748b'
}

function makeIcon(m) {
  const opacite = m.actif === false ? 0.5 : 1
  return L.divIcon({
    className: 'jirama-marker',
    html: `<span style="display:block;width:22px;height:22px;border-radius:9999px;background:${couleurDe(m)};border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.5);opacity:${opacite}"></span>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -12],
  })
}

// Le popup est construit en DOM (textContent) : aucune donnée n'est injectée comme HTML.
function buildPopup(m) {
  const root = document.createElement('div')
  root.style.minWidth = '180px'

  const ligne = (texte, gras = false) => {
    const p = document.createElement('p')
    p.textContent = texte
    p.style.margin = '2px 0'
    if (gras) p.style.fontWeight = '700'
    root.appendChild(p)
  }

  ligne(m.reference, true)
  ligne(m.nom)
  if (m.secteur) ligne(`Secteur : ${m.secteur}`)
  ligne(`Puissance : ${m.puissance} kVA`)
  ligne(`Statut : ${STATUT_OPERATIONNEL_LABELS[m.statut_operationnel] ?? '—'}`)
  ligne(`Charge : ${formatPourcent(m.taux_charge)}`)
  ligne(`État technique : ${ETAT_LABELS[m.etat] ?? m.etat}`)
  ligne(`Priorité : ${PRIORITE_LABELS[m.priorite] ?? '—'}`)
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

function draw() {
  if (!map) return
  layer.clearLayers()

  const points = []
  for (const m of props.markers) {
    const latlng = [m.latitude, m.longitude]
    points.push(latlng)
    L.marker(latlng, { icon: makeIcon(m) }).bindPopup(buildPopup(m)).addTo(layer)
  }

  if (points.length === 1) {
    map.setView(points[0], props.zoom)
  } else if (points.length > 1) {
    map.fitBounds(points, { padding: [40, 40] })
  }
}

onMounted(() => {
  map = L.map(container.value).setView(CENTRE_ANTSIRABE, 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map)
  layer = L.layerGroup().addTo(map)

  draw()
  // La taille du conteneur peut changer après le premier rendu.
  setTimeout(() => map && map.invalidateSize(), 200)
})

watch(() => [props.markers, props.colorBy], draw, { deep: true })

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <!-- relative + z-0 : crée un contexte d'empilement pour que la carte reste sous la sidebar et les modales -->
  <div ref="container" class="relative z-0 h-full w-full rounded-xl"></div>
</template>