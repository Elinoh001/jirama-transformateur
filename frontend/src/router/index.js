import { createRouter, createWebHistory } from 'vue-router'

import AuthLayout from '@/layouts/AuthLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { useAuthStore } from '@/stores/authStore'

const routes = [
  {
    path: '/login',
    component: AuthLayout,
    meta: { guest: true },
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('@/views/LoginView.vue'),
        meta: { title: 'Connexion' },
      },
    ],
  },
  {
    path: '/',
    component: DefaultLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: { name: 'dashboard' } },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: 'Tableau de bord' },
      },
      {
        path: 'transformateurs',
        name: 'transformateurs',
        component: () => import('@/views/TransformateursView.vue'),
        meta: { title: 'Transformateurs' },
      },
      {
        path: 'transformateurs/:id(\\d+)',
        name: 'transformateur-detail',
        component: () => import('@/views/TransformateurDetailView.vue'),
        meta: { title: 'Détail du transformateur' },
      },
      {
        path: 'charge',
        name: 'charge',
        component: () => import('@/views/ChargeView.vue'),
        meta: { title: 'Suivi de charge' },
      },
      {
        path: 'inspections',
        name: 'inspections',
        component: () => import('@/views/InspectionsView.vue'),
        meta: { title: 'Inspections' },
      },
      {
        path: 'interventions',
        name: 'interventions',
        component: () => import('@/views/InterventionsView.vue'),
        meta: { title: 'Interventions' },
      },
      {
        path: 'pannes',
        name: 'pannes',
        component: () => import('@/views/PannesView.vue'),
        meta: { title: 'Pannes' },
      },
      {
        path: 'carte',
        name: 'carte',
        component: () => import('@/views/MapView.vue'),
        meta: { title: 'Carte des transformateurs' },
      },
      {
        path: 'utilisateurs',
        name: 'utilisateurs',
        component: () => import('@/views/UtilisateursView.vue'),
        meta: { title: 'Utilisateurs', roles: ['ADMIN'] },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Token présent mais utilisateur pas encore chargé (ex : rechargement de la page).
  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchCurrentUser()
    } catch {
      auth.logout()
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  // Routes réservées à certains rôles : meta: { roles: ['ADMIN'] }
  if (to.meta.roles && !to.meta.roles.includes(auth.role)) {
    return { name: 'dashboard' }
  }
})

router.afterEach((to) => {
  document.title = to.meta.title
    ? `${to.meta.title} - JIRAMA Transformateurs`
    : 'JIRAMA Transformateurs'
})

export default router